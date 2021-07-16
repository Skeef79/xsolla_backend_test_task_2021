import requests
from requests.api import request
from random import random

BASE = "http://127.0.0.1:5000/"


#adding multiple products

for i in range(12,13):
    response = requests.post(BASE + "api/v1/products", data = {"sku": str(i), "name": f"name{i}", "type": "test", "price": str(random())})
    print(response.json())


#response = requests.post(BASE + 'api/v1/products', data = {'sku': 'G-5-40', 'name': 'CS:GO', 'type': 'game', 'price': '11.5'})
#response = requests.patch(BASE + 'api/v1/products', data = {'id':'1', 'price': '13'})




