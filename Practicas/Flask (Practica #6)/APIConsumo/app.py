import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"

print("\nGET:")
res = requests.get(API_URL)
titulo = res.json()[0]['title']
print(res.json()[0])
print("Titulo: " + titulo)

print("\nPOST:")
nueva_resena = {
    "title": "McDonalds",
    "body": "Excelentes nuggets",
    "userId": 1
}
res = requests.post(API_URL, json=nueva_resena)
print(res.json())

print("\nPUT:")
mod_resena = {
    "title": "KFC",
    "body": "Excelentes presas",
    "userId": 1
}
res = requests.put(f"{API_URL}/1", json=mod_resena)
print(res.json())

print("\nDELETE:")
res = requests.delete(f"{API_URL}/1")
print("Codigo de estado:", res.status_code)