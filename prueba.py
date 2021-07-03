import requests

files = {'upload_file': open('/home/mario/Downloads/prueba.txt','rb')}
r = requests.post("http://localhost:8080", files=files)
