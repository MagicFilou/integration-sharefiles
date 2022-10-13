import tempfile

import os
from dropbox import dropbox
from dropbox.files import FileMetadata

from datetime import datetime
from utils.transform import columns_dict_to_string

from sources import Source

class Node:
    def __init__(self, index, payload=None, parent=None):
        self.payload = payload
        self.index = index
        self.children = {}
        self.parent = None

    def set_child(self, node):
        if node.index not in self.children:
            self.children[node.index] = node
            node.parent = self

    def has_child(self, index):
        return index in self.children

    def get_child(self, index):
        return self.children[index]

    def print(self, level=0, verbose=False):
        st = "   " * level + self.index
        if verbose and self.payload:
            v_string = ""
            for k in self.payload:
                v_string += "{key}:{value} ".format(key=k, value=self.payload[k])
            st += f"<{v_string}>"
        print(st)

        for child in self.children.values():
            child.print(level + 1, verbose=verbose)


class FileSystem:
    def __init__(self):
        self.root = Node("root")

    def print(self, verbose=False):
        self.root.print(verbose=verbose)


class DropboxIndexer:
    def __init__(self, dbx):
        self.dbx = dbx
        self.fs = FileSystem()
        self.flat_files = {}
        self.folders = {}

#    def download(self, file_id):
    def download(self, path):
        #node = self.flat_files[file_id]

        # This will be deleted when the handled is closed.
        # extention_array = node.payload["display_path"].split('.')     
        extention_array = path.split('.')     
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=f".{extention_array[1]}")
        #get extention of the original file and add it to the destination file
        
        # self.dbx.files_download_to_file(tf.name, node.payload["display_path"])
        self.dbx.files_download_to_file(tf.name, path)
        return tf

    def _scan(self, response):
        for entry in response.entries:

            elements = [p for p in entry.path_lower.split("/") if p]
            node = self.fs.root
            for element in elements:
                if node.has_child(element):
                    node = node.get_child(element)
                else:
                    # Test the type of the node.
                    entry_type = "folder"
                    file = {}
                    if type(entry) == FileMetadata:
                        entry_type = "file"
                        file = {
                            "size": entry.size,
                            "is_downloadable": entry.is_downloadable,
                            "export_info": entry.export_info,
                            "client_modified": entry.client_modified,
                            "server_modified": entry.server_modified,
                        }
                    child = Node(
                        element,
                        payload={
                            "path": entry.path_lower,
                            "display_path": entry.path_display,
                            "name": entry.name,
                            #for some reason id is with the format 'id:myidsomething'
                            "id": entry.id.split(':')[1],
                            "type": entry_type,
                            "file": file,
                        },
                    )
                    node.set_child(child)
                    node = child

                    if entry_type == "file":
                        self.flat_files[entry.id] = node
                    if entry_type == "folder":
                        self.folders[entry.id] = node

    def build_index(self):
        dbx = self.dbx

        # Go through all the files in the dropbox.
        response = dbx.files_list_folder(
            "",  # Path. Empty string means root folder.
            recursive=True,  # Yes to subfolders.
            include_non_downloadable_files=True,  # Yes to Google Docs etc.
        )
        self._scan(response)
        while response.has_more:
            response = dbx.files_list_folder_continue(response.cursor)
            self._scan(response)
        # self.fs.print(True)



class DropboxSource(Source):
    def __init__(self, credentials, sourceName, integrationID):
        super().__init__(credentials, sourceName, integrationID)

    def run_index(self):
        dbx = dropbox.Dropbox(oauth2_access_token=self.credentials["access_token"])
        d_index = DropboxIndexer(dbx)
        d_index.build_index()

        for folder in d_index.folders.values():
            payload = folder.payload                  
           
            index = {
                "id": payload["id"],
                "type": payload["type"],                
                "name": payload["name"],
                "size": 0,
                "path": payload["path"],                
                "last_indexed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if folder.parent.payload is not None:
                index['parent'] = folder.parent.payload["path"]
            yield index
            

        for file in d_index.flat_files.values():
            payload = file.payload        
            content_type="downloadable"
            if not payload["file"]["is_downloadable"]:
                content_type="readable"
            index = {
                "id": payload["id"],
                "type": payload["type"],                
                "name": payload["name"].split('.')[0],
                "extension": f".{payload['name'].split('.')[1]}",
                "size": payload["file"]["size"],
                "path": payload["path"],                
                "updated_client": payload["file"]["client_modified"].strftime("%Y-%m-%d, %H:%M:%S"),
                "updated_server": payload["file"]["server_modified"].strftime("%Y-%m-%d, %H:%M:%S"),
                "last_indexed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content_type": content_type,
            }
            if file.parent.payload is not None:
                index['parent'] = file.parent.payload["path"]
            yield index

        

    def run_content(self, fileList):
        dbx = dropbox.Dropbox(oauth2_access_token=self.credentials["access_token"])
        d_index = DropboxIndexer(dbx)
        for file in fileList:
            path = file["path"]
            ft = None
            try:
                ft = d_index.download(path)
            #Dropbox error could raise
            except:
                print("Exception has occured")

            
            yield ft, file["generated_id"], file["dataset_name"], file["path"]
        
