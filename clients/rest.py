import requests




def restCall(url, headers, expects):
  resp = requests.get(url, headers=headers)
  
  if expects == "json":
    return resp.json()

