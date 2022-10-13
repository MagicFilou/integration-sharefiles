import magic
import os
from datetime import datetime
from handlers import Handler

from datetime import datetime    

from parsers import Parser
from clients.redis import save_structure_redis, save_package_redis
from utils.strings import random_string
from utils.constants import MODE_MAGIC, TYPE_FOLDER, MAX_SIZE_BYTES

from settings import C


#TODO replace global scopefull_parser_list by a state in populate_parsers function
full_parser_list = []

def populate_parsers(parser_class ):
    """Popupale_parsers is a recursive function that establishes the list of available parsers.

    param: parser_class is used because it is recursive you give the class to get its children
    """
    parsers = parser_class.__subclasses__()
    if len(parsers)>0:
        full_parser_list.append(parser_class)
        for p in parsers:
            populate_parsers(p)
    else:
        full_parser_list.append(parser_class)


def find_parser(filetype):
    """Find_parser finds the parser depending on the file type.

    param filetype: can be a mimetype or a an extension to get the corresponding parser
    """
    for parser in full_parser_list:
        if filetype in parser.ACCEPTED_TYPES:
            print("parser_found")
            return parser

def findDatasetInfoForField(datasets, parent):
  for index, dataset in enumerate(datasets):
    if dataset["path"] == parent:
      return index, dataset["name"]
  return -1, ""

class ShareFileHandler(Handler):
  def scan_structure_runner(self, source):
    fileList = []
    shareFile = dict()
    shareFile["integration_id"] = source.integrationID
    shareFile["name"] = source.name
    #probably should be a different name
    shareFile["tables"] = []

    now = datetime.now()

    # always have a root
    ds = dict()
    ds = {
      "integration_id": source.integrationID,
      "name": "root",
      "fields": [],
      "found": now.strftime("%Y-%m-%dT%H:%M:%S.0000000+02:00"),
      "source_type": TYPE_FOLDER,
      "path": "/"
    }
    shareFile["tables"].append(ds)
    print("Start building the right structure")
    for index in source.run_index():
      #for each index intem just insert it into a postgres
      if "parent" not in index:
        index["parent"]= "/"
      if len(index["parent"]) == 0:
        index["parent"]= "/"
      if index["type"] == TYPE_FOLDER:
        ds = {
        "integration_id": source.integrationID,
        "name": index["name"],
        "fields": [],
        "found": now.strftime("%Y-%m-%dT%H:%M:%S.0000000+02:00"),
        "path": index["path"],
        "source_type": index["type"]
        }
        shareFile["tables"].append(ds)     
      # will have an issue if get the folder for a file after this one but will test that scenario
      else:
        generatedId = random_string(10)
        datasetIndex, datasetName = findDatasetInfoForField(shareFile["tables"], index["parent"])
        if datasetIndex==-1:
          print("ERROR - file with no dataset:"+ index["path"])
        
        field  = {
          "integration_id": source.integrationID,
          "name": index["path"],
          "display_name": index["name"],
          "found": now.strftime("%Y-%m-%dT%H:%M:%S.0000000+02:00"),
          "generated_id": generatedId
          # "size": f"{str(index['size'])}B",
        }

        if "type" in index:
          field["type"] = index["type"]
        else:
          _, file_extension = os.path.splitext(index["path"])
          field["type"] = file_extension[1:]

        file = {
          "path": index["path"],
          "generated_id": generatedId,
          "dataset_name": datasetName,
          "id": index["id"],
          "downloadable": True,
          "type": index["type"]
        }

        if "size" in index:
          field["size"] = f"{str(index['size'])}B"
          if int(index['size']) > MAX_SIZE_BYTES:
            file["downloadable"] = False

        shareFile["tables"][datasetIndex]["fields"].append(field)
        # add to file list
        fileList.append( file)
      
      # check_and_insert(index, collection_name, DATA_INDEX_UNIQUE_KEYS)
    print(shareFile)
    save_structure_redis(shareFile)
    return fileList


  def scan_content_runner(self, source, fileList):
      populate_parsers(Parser)
      #remove the first element which is an absract Parser class might not be necessary
      full_parser_list.pop(0)


      for tf, generated_id, dataset_name, field_name in source.run_content( fileList):
          # Here we have a file.
          #file_name, file_extension = os.path.splitext(tf.name)
          _, file_extension = os.path.splitext(tf.name)
          if C["ModeType"] == MODE_MAGIC:              
              mimetype = magic.from_file(tf.name, mime=True)
              file_type = mimetype
          else:        
              file_type = file_extension

          # Lookup a parser passed on the mimetype.
          # Should be exclusive list per parser btw
          parser_class = find_parser(file_type)
          if parser_class:
            package = dict()
            package = {
              "integration_id": source.integrationID,
              "dataset": dataset_name,  
              "items": []            
            }         
            #instanciate an item of the class
            parser = parser_class(source)
            for text, position in parser.parse(tf.name):
              package["items"]= []
              # text, meta = parsed_element
              # Could extract more data but stick with the position
              package["index"] = str(position)
              field = {
                "field_id": generated_id, 
                "field_name": field_name,
                "value": text,
              }
              package["items"].append(field)
              save_package_redis(package)
            
          else: 
            print("File type", file_type)
            print("Parser not found, extention or mimetype not supported")
          tf.close() # This will now be deleted.