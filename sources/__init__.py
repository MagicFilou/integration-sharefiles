from utils.constants import SEPARATOR

class Source:
    def __init__(self, credentials, sourceName, integrationID):
        self.name = sourceName
        self.integrationID = int(integrationID)
        self.credentials = credentials
    

    def run_structure(self, collection_name):
        #Overide this to continue with:
        #creating a structure/index table in the default database
        #save to redis in order for the backend to create the corresponding collections
        pass

    def run_index(self):
        #Overide this :
        #Populate the index table created in structure
        pass

    def run_content(self):
        #Overide this :
        #Create the content table and populate the content of each relevant data into the default db
        pass