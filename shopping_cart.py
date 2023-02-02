import datetime
import time
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, fields, marshal_with
from flask import Flask, redirect, url_for
import requests
import random



app = Flask(__name__)
api = Api(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_cart_db.sqlite3' # db.sqlite3 is the database name, aka. file name
app.app_context().push()
db = SQLAlchemy(app)


# API URLs
get_single_user_url    = 'https://fakestoreapi.com/users/'
get_single_product_url = 'https://fakestoreapi.com/products/'


def get_single_product(product_id):
    # url = get_single_product_url + str(product_id)
    url = f'https://fakestoreapi.com/products/{str(product_id)}'
    r   = requests.get(url)
    return r.json()
    # return {
    #     'product_id': product_id,
    #     'title': request.get('title'),
    #     'description': request.get('description'),
    #     'price': request.get('price'),
    # }



def get_single_user(user_id):
    url = get_single_user_url + str(user_id)
    r   = requests.get(url)

    return r.json()
    # return {
    #     'user_id': user_id,
    #     'username': request.get('username')
    # }


# Models #

class ShoppingCart(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, auto_increment=True)
    # To be replaced with the User relationship
    user_id    = db.Column('user_id', db.Integer)
    username   = db.Column('username', db.String)
    # To be replaced with the Product relationship
    product_id = db.Column('product_id', db.Integer)
    product_title = db.Column('product_title', db.String)
    product_desc = db.Column('product_desc', db.String)
    product_price = db.Column('product_price', db.Integer)

    quantity = db.Column('quantity', db.Integer)
    auto_date = db.Column('auto_date', db.DateTime, default=datetime.datetime.now)


shopping_cart_fields = {
    'id': fields.Integer,

    'user_id': fields.String,
    'username': fields.String,
    
    'product_id': fields.Integer,
    
    'product_title': fields.String,
    'product_desc': fields.String,
    'product_price': fields.Integer,
    
    'quantity': fields.Integer,
    'auto_date': fields.DateTime,

}

#
# Generate fake data
# 
# @app.route('/fake')
# def FakeDataData():
#     for _ in range(300):
#         gen_product = get_single_product(random.randint(1, 20))
#         gen_user    = get_single_user(random.randint(1, 10))
#         quantity    = random.randint(1, 5)
        

#         new_cart = ShoppingCart(user_id=gen_user['id'], username=gen_user['username'], \
#                                 product_id=gen_product['id'], \
#                                 product_title=gen_product['title'], \
#                                 product_desc=gen_product['description'], \
#                                 product_price=gen_product['price'], quantity=quantity)
#         db.session.add(new_cart)
#         db.session.commit()
        
#         print("Cart created", new_cart)

#     return 'Done!'


class CartsList(Resource):
    @marshal_with(shopping_cart_fields)
    def get(self):
        users = ShoppingCart.query.all()

        return users


class GetCartByUserID(Resource):
    @marshal_with(shopping_cart_fields)
    def get(self):
        pass



api.add_resource(CartsList, '/carts_list')
# api.add_resource(FakeDataData, '/fake')

if __name__ == '__main__':
    # db.destroy_all()
    db.create_all()
    app.run(debug=True)