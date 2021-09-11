import requests

url = 'http://127.0.0.1:1080/search'
body = {
    "Query": "SolveMaze issues with debugger",
    "k": 2
}
response = requests.post(url, data=body)
print(response.json())
