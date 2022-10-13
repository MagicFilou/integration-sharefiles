
import json

# This might need to change, but attemp to control the various sources.
from handlers.sharefiles import ShareFileHandler
from sources.dropbox import DropboxSource
from sources.google_drive import DriveSource

from utils.constants import  PATH, SOURCE_DROPBOX, SOURCE_DRIVE

from settings import C


def dropbox_runner(credentials):
    main_runner(DropboxSource(credentials, C["Source"], C["IntegrationID"]), ShareFileHandler())

def driver_runner(credentials):
    main_runner(DriveSource(credentials, C["Source"], C["IntegrationID"]), ShareFileHandler())

def main_runner(source, handler):

    print("run_structure")
    fileList = handler.scan_structure_runner(source)

    print("run_content")
    handler.scan_content_runner(source, fileList)
    

# if __name__ == '__main__':
#     {'access_token': 'jpU0HRis7r0AAAAAAAAAAXLuDHF6YagjpYg6G1FkrQiQJWNfHcefvkjEuBIH7dS5', 'token_type': 'bearer', 'uid': '3656399888', 'account_id':
# 'dbid:AAD1m3Hj4sU8lqfgcIsM99EnV7hrxVMtWhk', 'scope': 'account_info.read files.content.read files.content.write files.metadata.read files.metadat
# a.write'}
    #"eyJraWQiOiJqVHJLczM2V1BVSjA1SkZuU3h6ZldRV2VielVPeERPVVVJV0ZcL25pRXd4az0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzNjQyZmM1Mi01ZjJhLTRiMTAtOWE0NS03NThkOWQ4MThmZDMiLCJhdWQiOiI1MG0wOGhwdmMyb2sxZTFrb2oxcGI5M2hyciIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjEyYWU1MmM5LWJmYWItNGE0ZC04NjA3LTQ4NzE2MGYzNTJlOSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjA0NTgwNjgwLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV84MjVXQzJxSmgiLCJjb2duaXRvOnVzZXJuYW1lIjoiMzY0MmZjNTItNWYyYS00YjEwLTlhNDUtNzU4ZDlkODE4ZmQzIiwiZXhwIjoxNjA0NTg0MjgwLCJpYXQiOjE2MDQ1ODA2ODAsImVtYWlsIjoicGhpbGlwcGUubXVyaXNvbit3dWx0eUB3dWx0LmlvIn0.GFBcACcUHZrTIJO6VkqFPW73_czFpd01JIkSy-htl0v6LTG-alA09FDaKVzmmipgag2JkmWfFLD7Ec2y6gV0D19CfgGJYJcRODgqzZfwX90GjG2gz-8C0ghLUtYKyMd_UT7h3gD8D9SijC7V40Af89OgbGdBb2RMjsHkjPTW-pSF3_YzG4D8P9AGlUSTrmTRuJFY_pDLjxCaiRnxfXEwHHdrsnxcGOdiLlbwHxlFSyXeyPJh4igWP7mrb8NAfBtcSkaEwLgCkBedeO-LhF1k-yC_d5MicxYmP98kmNezI9VdeP7KjgCDI2DDMJ2MRUHDmWaBLx2YLAMwIf116_hRvQ"

#for pipedrive test
#token = "be8cac8c3e3ca2f6949012789cfa4202e983a49b"

func_runner =  {
    SOURCE_DROPBOX: dropbox_runner,
    SOURCE_DRIVE: driver_runner,
}[C["Source"]]

func_runner({"access_token":C["Token"]})

