from random import expovariate
import tempfile

import os
from io import BytesIO, FileIO

from datetime import datetime
from utils.constants import TYPE_FOLDER
from utils.transform import columns_dict_to_string

from settings import C
from clients.rest import restCall

from sources import Source

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def get_type_and_name(mimeType, fileName):
    googleTypes = {
    "application/vnd.google-apps.folder":TYPE_FOLDER,
    "application/vnd.google-apps.spreadsheet":"google_sheet",
    "application/vnd.google-apps.document":"google_doc", 
    "application/vnd.google-apps.presentation":"google_presentation"
    }    
    type = googleTypes.get(mimeType, "other")

    if type == "other":
        split = fileName.split('.')
        return split[-1], ".".join(split[0:len(split)-1])

    return type, fileName



def build_folder_index(listFiles):
    index=0
    listFolders = {}
    while True:
        if listFiles[index]["mimeType"] != "application/vnd.google-apps.folder" or index >= len(listFiles):
            break
        index+=1
    
    for file in listFiles[0:index]:
        file["type"]= TYPE_FOLDER
        listFolders[file["id"]] = file
    
    rootID = ""
    for fileID in listFolders:
        if listFolders[fileID]["parents"][0] not in listFolders:
            rootID=listFolders[fileID]["parents"][0]
            break
    
    listFolders[rootID]= {
        "id": rootID,
        "type": TYPE_FOLDER,
        "path": "",
        "parents": ["root"]
    }
    queue = [rootID]

    # loop and build path
    while True:
        try:
            currentID = queue.pop(0)    
            for fileID in listFolders:
                if "parents" in listFolders[fileID]:
                    if listFolders[fileID]["parents"][0] == currentID:
                        queue.append(fileID) 
                        listFolders[fileID]["parent"] = listFolders[currentID]["path"]
                        listFolders[fileID]["path"] = listFolders[fileID]["parent"]+"/"+ listFolders[fileID]["name"]
        except IndexError as ex:
            print(ex, "FINISHED QUEUE")
            break
    
    return index, listFolders, rootID


class DriveSource(Source):
    def __init__(self, credentials, sourceName, integrationID):
        super().__init__(credentials, sourceName, integrationID)

    def run_index(self):
        print("index drive")

        # Should probably replace that with the python client...
        URL_files = "https://www.googleapis.com/drive/v3/files?fields=files/name,files/id,files/parents,files/mimeType,files/sharedWithMeTime,files/size&orderBy=folder,createdTime"

        headers = {
        "Authorization": f"Bearer {C['Token']}"
        }
        d_index = restCall(URL_files, headers, "json")

        if d_index:
            fileIndex, listFolders, rootID = build_folder_index(d_index["files"])

            listFiles = d_index["files"][fileIndex:]
            toRemove = []

            for index, file in enumerate(listFiles):
                # so far do not consider the shared with me files
                if "sharedWithMeTime" in file:
                    toRemove.append(index)  
                    continue
                if "parents" not in file:
                    toRemove.append(index)  
                    continue

                file["parent"] = listFolders[file["parents"][0]]["path"]
                file["path"] = file["parent"]+ "/" + file["name"]
                file["type"], file["name"]  = get_type_and_name(file["mimeType"], file["name"])
                file["id"] = file["id"]

            #remove all shared files
            toRemove.sort(reverse=True)
            for index in toRemove:
                del listFiles[index]

            #should revise later on if that becomes necessary or not
            listFolders.pop(rootID, None)
            for key in listFolders:
                if "sharedWithMeTime" not in listFolders[key]:
                    yield listFolders[key]

            for file in listFiles:
                yield file

          

        

    def run_content(self, fileList):
        print("run content")
        creds = Credentials(C['Token'])
        service  = build("drive", "v3", credentials=creds)
        
        for file in fileList:
            print(file)
            if file["downloadable"]:
                exportMime = "none"
                exportSuffix = f".{file['type']}"
                if file["type"] == "google_doc":
                    exportMime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    exportSuffix=".docx"
                elif file["type"] == "google_presentation":
                    exportMime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    exportSuffix=".pptx"
                elif file["type"] == "google_sheet":
                    exportMime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    exportSuffix=".xlsx"
                if exportMime != "none":
                    request = service.files().export_media(fileId=file["id"],
                                    mimeType=exportMime)
                else:
                    request = service.files().get_media(fileId=file["id"])

                tf = tempfile.NamedTemporaryFile(delete=False, suffix=exportSuffix)
                fh = FileIO(tf.name, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                try:
                    while done is False:
                        status, done = downloader.next_chunk()
                        print ("Download %d pct." % int(status.progress() * 100))
                    yield tf, file["generated_id"], file["dataset_name"], file["path"]
                except Exception as e:
                    print('Error downloading file', file["dataset_name"], file["path"], e)