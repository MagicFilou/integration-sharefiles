from os import getenv as env

C = dict()

C["ENV"] = env('ENV',"notprod")
C["IntegrationID"] = env('INTEGRATION_ID')
C["CompanyID"] = env('COMPANY_ID')

C["Redis"] = dict()
C["Redis"]["Host"] = env('REDIS_HOST', 'localhost')
C["Redis"]["Port"] = int(env('REDIS_PORT', 6379))
C["Redis"]["Database"] = int(env('REDIS_DATABASE', 0))

C["StructureOutputKey"] = f"{env('STRUCTURE_KEY')}:{C['CompanyID']}:{C['IntegrationID']}"
C["ContentOutputKey"] = f"{env('CONTENT_KEY')}:{C['CompanyID']}:{C['IntegrationID']}"

C["Source"] = env('SOURCE', 'dropbox')
C["Token"] = env('TOKEN', 'token')
# C["UserID"] = env('USER_ID', '')

# magic|extension
C["ModeType"]= env('MODE_TYPE', 'magic')

