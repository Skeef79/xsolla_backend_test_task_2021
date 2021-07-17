from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy, model
import os

app = Flask(__name__)
api = Api(app)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ProductModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(), unique=True, nullable = False)
    name = db.Column(db.String(), nullable = False)
    _type = db.Column(db.String(), nullable = False)
    price = db.Column(db.Float, nullable = False)

    def __repr__(self):
        return f'Product(sku = {self.sku}, name = {self.name}, type = {self._type}, price = {self.price}'


product_post_args = reqparse.RequestParser()
product_post_args.add_argument('sku', type = str, help = 'Product SKU is required', required = True)
product_post_args.add_argument('name', type = str, help = 'Product name is required', required = True)
product_post_args.add_argument('type', type = str, help = 'Product type is required', required = True)
product_post_args.add_argument('price', type = float, help = 'Product price is required', required = True)

product_patch_args = reqparse.RequestParser()
product_patch_args.add_argument('sku', type = str, help = 'Product SKU')
product_patch_args.add_argument('name', type = str, help = 'Product name')
product_patch_args.add_argument('type', type = str, help = 'Product type is required')
product_patch_args.add_argument('price', type = float, help = 'Product price')

products_get_args = reqparse.RequestParser()
products_get_args.add_argument('sort_by',type = str, help = 'Sort items by fields')
products_get_args.add_argument('filter_by', type = str, help = 'Filter items by fields')

resource_fields = {
	'id': fields.Integer,
    'sku': fields.String,
	'name': fields.String,
	'_type': fields.String,
	'price': fields.Float
}


def getProductByID(product_id):
    result = ProductModel.query.filter_by(id = product_id).first()
    if not result:
        return None, 404, 'Could not find product with that id'
    
    return result, 200, None


def getProductBySKU(sku):
    result = ProductModel.query.filter_by(sku = sku).first()
    if not result:
        return None, 404, 'Could not find product with that sku'

    return result, 200, None


def getProduct(args, id, sku):
    if id:
        product, status_code, message = getProductByID(id)
    else:
        product, status_code, message = getProductBySKU(sku)

    if not product:
        abort(status_code, message = message)

    return product, status_code


def postProduct(args):
    product = None
    if args['sku']:
        product = ProductModel.query.filter_by(sku = args['sku']).first()
         
    if product:
        abort(409, message = 'product with that sku already exists')


    new_product = ProductModel(sku = args['sku'], name = args['name'], _type = args['type'], price = args['price'])
    db.session.add(new_product)
    db.session.commit()

    return {'id': new_product.id}, 201


def patchProduct(args, id, sku):
    if id:
        product, status_code, message = getProductByID(id)
    else:
        product, status_code, message = getProductBySKU(sku)

    if not product:
        abort(status_code, message = message)
    
    if args['name']:
        product.name = args['name']
    if args['type']:
        product._type = args['type']
    if args['price']:
        product.price = args['price']

    db.session.commit()
    return product, 200


def deleteProduct(args, id, sku):
    if id:
        product, status_code, message = getProductByID(id)
    else:
        product, status_code, message = getProductBySKU(sku)

    if not product:
        abort(status_code, message = message)

    db.session.delete(product)
    db.session.commit()

    return '', 204


class ProductID(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        return getProduct(None, id, None)

    @marshal_with(resource_fields)
    def patch(self, id):
        args = product_patch_args.parse_args()
        return patchProduct(args, id, None)

    def delete(self, id):
        return deleteProduct(None, id, None)


def getProductsList(args):
    
    products = ProductModel.query.all()
    return products
    

class ProductSKU(Resource):
    @marshal_with(resource_fields)
    def get(self, sku):
        return getProduct(None, None, sku)

    @marshal_with(resource_fields)
    def patch(self, sku):
        args = product_patch_args.parse_args()
        return patchProduct(args, None, sku)

    def delete(self, sku):
        return deleteProduct(None, None, sku)


class ProductList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = products_get_args.parse_args()
        return getProductsList(args)

    def post(self):
        args = product_post_args.parse_args()
        return postProduct(args)

        
api.add_resource(ProductID, '/api/v1/products/id/<int:id>')
api.add_resource(ProductSKU, '/api/v1/products/sku/<string:sku>')
api.add_resource(ProductList, '/api/v1/products')

if __name__ == '__main__':
    app.run()
