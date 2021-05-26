from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, abort, reqparse, marshal_with, fields

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

product_add_args = reqparse.RequestParser()
product_add_args.add_argument('name', type=str, required=True)
product_add_args.add_argument('description', type=str, required=True)
product_add_args.add_argument('price', type=float, required=True)
product_add_args.add_argument('qty', type=int, required=True)

resource_field = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'price': fields.Float,
    'qty': fields.Integer,
}

class ProductList(Resource):
    
    @marshal_with(resource_field)
    def get(self):
        all_products = Product.query.all()
        if not all_products:
            abort(404, message="Don't have product")
        return all_products, 201

    @marshal_with(resource_field)
    def post(self):
        args = product_add_args.parse_args()
        new_product = Product(args['name'], args['description'], args['price'], args['qty'])

        db.session.add(new_product)
        db.session.commit()
        return new_product, 201

class ProductSelect(Resource):

    @marshal_with(resource_field)
    def get(self, product_id):
        # product = Product.query.filter_by(id=product_id).first()
        product = Product.query.get(product_id)
        if not product:
            abort(404, message='Not found product !!!')
        return product, 201

    @marshal_with(resource_field)
    def put(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Don't have product for update")
        args = product_add_args.parse_args()

        product.name = args['name']
        product.description = args['description']
        product.price = args['price']
        product.qty = args['qty']

        db.session.commit()
        return product, 201

    @marshal_with(resource_field)
    def delete(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Don't have product for delete")
        db.session.delete(product)
        db.session.commit()
        return product, 201


api.add_resource(ProductList, '/product')
api.add_resource(ProductSelect, '/product/<int:product_id>')


if __name__ == '__main__':
    app.run(debug=True)