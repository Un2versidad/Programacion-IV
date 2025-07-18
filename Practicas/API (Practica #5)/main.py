import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"

print("\nGET:")
res = requests.get(API_URL)
tit = res.json()[0]['title']
print(f"Primer título: {tit}")
print(res.json()[0])
print("\nPOST")

nueva_resena = {
    "titule" : "Mcdonalds",
    "body" : "Excelentes nuggets",
    "userid" : 1
    
}

res = requests.post(API_URL, json=nueva_resena)
print(res.json())

print("\nPUT")
mod_resena = {
    "titule" : "KFC",
    "body" : "Excelentes presas",
    "userid" : 1
}
res = requests.put(f"{API_URL}/1", json=mod_resena)
print(res.json())

print("\nDELETE")
res = requests.delete(f"{API_URL}/1")
print("Codigo de estado:" , res.status_code)
