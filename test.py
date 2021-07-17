import requests
import uuid
import random
from requests.api import request

from requests.models import Response

BASE = 'http://127.0.0.1:5000/api/v1/products'
names = ['Dota 2', 'CS:GO', 'Valorant', 'Minecraft', 'Stronghold', 'Warcraft 3', 'Tarkov', 'Call of Duty']
types = ['Game', 'T-Shitr', 'Cards', 'Hoodie', 'Cap', 'Pants', 'Jacket', 'Currency']


def randomName():
    return random.choice(names)

def randomType():
    return random.choice(types)

def randomPrice():
    return random.randint(0,40) + random.random()

def randomSKU():
    return str(uuid.uuid4())

def randomProduct():
    return {
        'sku': randomSKU(),
        'name': randomName(),
        'type': randomType(),
        'price': randomPrice()
    }


product = randomProduct()

def isProduct(result):
    assert 'id' in result
    assert 'sku' in result
    assert 'name' in result
    assert '_type' in result
    assert 'price' in result
    assert len(result) == 5


def test_get_list():
    response = requests.get(BASE)
    assert response.status_code == 200
    result = response.json()
    if len(result)!=0:
        for product in result:
            isProduct(product)


def test_post_new_product():
    response = requests.post(BASE, data = product)
    assert response.status_code == 201
    

    result = response.json()
    assert 'id' in result
    assert len(result) == 1

    product['id'] = result['id']


def test_post_product_bad_params():
    response = requests.post(BASE)
    assert response.status_code == 400

    response = requests.post(BASE,data = {'name': 'test'})
    assert response.status_code == 400
    assert 'message' in response.json()
    assert len(response.json()) == 1

    response = requests.post(BASE, data = {'sku': randomSKU()})
    assert response.status_code == 400
    assert 'message' in response.json()
    assert len(response.json()) == 1

    response = requests.post(BASE,data = {'type': 'test'})
    assert response.status_code == 400
    assert 'message' in response.json()
    assert len(response.json()) == 1

    response = requests.post(BASE,data = {'price': '10'})
    assert response.status_code == 400
    assert 'message' in response.json()
    assert len(response.json()) == 1


def test_get_list_after_post():
    response = requests.get(BASE)
    assert response.status_code == 200
    result = response.json()
    if len(result)!=0:
        for product in result:
            isProduct(product)


def test_get_product_by_id():
    response = requests.get(f'{BASE}/id/{product["id"]}')
    assert response.status_code == 200

    result = response.json()
    isProduct(result)


def test_get_product_by_sku():
    response = requests.get(f'{BASE}/sku/{product["sku"]}')
    assert response.status_code == 200

    result = response.json()
    isProduct(result)


def test_post_product_with_used_sku():
    response = requests.post(BASE, data = {
        'sku': product['sku'],
        'name': product['name'],
        'type': product['type'],
        'price': product['price']
    })

    assert response.status_code == 409 


def test_patch_product_by_id():
    response = requests.patch(f'{BASE}/id/{product["id"]}', data = {})
    assert response.status_code == 200

    result = response.json()
    isProduct(result)

    new_name = randomName()
    new_type = randomType()
    new_price = randomPrice()

    response = requests.patch(f'{BASE}/id/{product["id"]}', data = {'name': new_name, 'type': new_type, 'price': new_price})
    assert response.status_code == 200

    result = response.json()
    isProduct(result)

    assert result['name'] == new_name
    assert result['_type'] == new_type
    assert result['price'] == new_price


def test_patch_product_id_not_exists():
    products = requests.get(BASE).json()
    idees = [product['id'] for product in products]
    response = requests.patch(f'{BASE}/id/{max(idees)+1}')
    assert response.status_code == 404
    assert 'message' in response.json()
    assert len(response.json()) == 1


def test_patch_product_by_sku():
    response = requests.patch(f'{BASE}/sku/{product["sku"]}', data = {})
    assert response.status_code == 200

    result = response.json()
    isProduct(result)

    new_name = randomName()
    new_type = randomType()
    new_price = randomPrice()

    response = requests.patch(f'{BASE}/sku/{product["sku"]}', data = {'name': new_name, 'type': new_type, 'price': new_price})
    assert response.status_code == 200

    result = response.json()
    isProduct(result)

    assert result['name'] == new_name
    assert result['_type'] == new_type
    assert result['price'] == new_price


def test_patch_product_sku_not_exists():
    response = requests.patch(f'{BASE}/sku/{randomSKU()}')
    assert response.status_code == 404
    assert 'message' in response.json()
    assert len(response.json()) == 1


def test_delete_product_by_id():
    new_product = randomProduct()
    response = requests.post(BASE, data = new_product)
    p_id = response.json()['id']
    response = requests.delete(f'{BASE}/id/{p_id}')
    assert response.status_code == 204
    

def test_delete_product_id_not_exist():
    products = requests.get(BASE).json()
    idees = [product['id'] for product in products]
    response = requests.delete(f'{BASE}/id/{max(idees)+1}')
    
    assert response.status_code == 404
    assert 'message' in response.json()
    assert len(response.json()) == 1


def test_delete_product_by_sku():
    new_product = randomProduct()
    response = requests.post(BASE, data = new_product)
    p_id = response.json()['id']
    response = requests.get(f'{BASE}/id/{p_id}')
    sku = response.json()['sku']

    response = requests.delete(f'{BASE}/sku/{sku}')
    assert response.status_code == 204


def test_delete_product_sku_not_exist():
    sku = randomSKU()
    response = requests.delete(f'{BASE}/sku/{sku}')

    assert response.status_code == 404
    assert 'message' in response.json()
    assert len(response.json()) == 1


def test_delete_product_final():
    response = requests.delete(f'{BASE}/id/{product["id"]}')

    assert response.status_code == 204
