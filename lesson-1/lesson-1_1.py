import requests
import json

req = requests.get("https://api.github.com/users/dkodnik/repos")

if req.status_code==200:
    data = json.loads(req.text)
    
    with open("github.json","w") as fout:
        json.dump(data, fout, indent=4)