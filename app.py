from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy, model

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class ProductModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(), unique=True, nullable = False)
    name = db.Column(db.String(), nullable = False)
    _type = db.Column(db.String(), nullable = False)
    price = db.Column(db.Float, nullable = False)

    def __repr__(self):
        return f'Product(sku = {self.sku}, name = {self.name}, type = {self._type}, price = {self.price}'


product_get_args = reqparse.RequestParser()
product_get_args.add_argument('id', type = int, help = 'Product id')
product_get_args.add_argument('sku', type = str, help = 'Product SKU')

product_post_args = reqparse.RequestParser()
product_post_args.add_argument('sku', type = str, help = 'Product SKU is required', required = True)
product_post_args.add_argument('name', type = str, help = 'Product name is required', required = True)
product_post_args.add_argument('type', type = str, help = 'Product type is required', required = True)
product_post_args.add_argument('price', type = float, help = 'Product price is required', required = True)

product_patch_args = reqparse.RequestParser()
product_patch_args.add_argument('id', type = int, help = 'Product id')
product_patch_args.add_argument('sku', type = str, help = 'Product SKU')
product_patch_args.add_argument('name', type = str, help = 'Product name')
product_patch_args.add_argument('type', type = str, help = 'Product type is required')
product_patch_args.add_argument('price', type = float, help = 'Product price')

product_delete_args = reqparse.RequestParser()
product_delete_args.add_argument('id', type = int, help = 'Product id')
product_delete_args.add_argument('sku', type = str, help = 'Product SKU')

resource_fields = {
	'id': fields.Integer,
    'sku': fields.String,
	'name': fields.String,
	'type': fields.String,
	'price': fields.Float
}


def getProduct(product_id, sku):
    if not product_id and not sku:
        return None, 404, 'You should pass either id or sku'

    if product_id and sku:
        return None, 404, 'You can pass either id or sky, not both'

    if product_id:
        result = ProductModel.query.filter_by(id = product_id).first()
        if not result:
            return None, 404, 'Could not find product with that id'
    else:
        result = ProductModel.query.filter_by(sku = sku).first()
        if not result:
            return None, 404, 'Could not find product with that sku'

    return result, 200, None


class Product(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = product_get_args.parse_args()
        product, status_code, message = getProduct(args['id'], args['sku'])

        if not product:
            abort(status_code, message = message)
        
        return product, status_code

    def post(self):
        args = product_post_args.parse_args()
        product = ProductModel.query.filter_by(sku = args['sku']).first()
        if product:
            abort(409, message = 'product with that sku already exists')

        new_product = ProductModel(sku = args['sku'], name = args['name'], _type = args['type'], price = args['price'])
        db.session.add(new_product)
        db.session.commit()

        return {'id': new_product.id}, 201

    @marshal_with(resource_fields)
    def patch(self):
        args = product_patch_args.parse_args()
        product, status_code, message = getProduct(args['id'], args['sku'])
        
        if not product:
            abort(status_code, message = message)
        
        if args['name']:
            product.name = args['name']
        if args['type']:
            product.type = args['type']
        if args['price']:
            product.price = args['price']

        db.session.commit()

        return product, 200

    def delete(self):
        args = product_delete_args.parse_args()
        product, status_code, message = getProduct(args['id'], args['sku'])
        if not product:
            abort(status_code, message = message)

        print(product)
        db.session.delete(product)
        db.session.commit()

        return '', 204


api.add_resource(Product, '/api/v1/products')

if __name__ == '__main__':
    app.run(debug = True)
