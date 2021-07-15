import requests
from requests.api import request

BASE = "http://127.0.0.1:5000/"

#response = requests.get(BASE + "api/v1/product", params={"id":1, "sku":"kek"})

#response = requests.post(BASE + 'api/v1/products', data = {'sku': 'G-5-40', 'name': 'CS:GO', 'type': 'game', 'price': '11.5'})
#response = requests.patch(BASE + 'api/v1/products', data = {'id':'1', 'price': '13'})

response = requests.delete(BASE + 'api/v1/products', data = {'id': '2'})
print(response)

print(response.json())


