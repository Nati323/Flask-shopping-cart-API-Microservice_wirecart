import datetime
import time
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, fields, marshal_with
from flask import Flask, Response, make_response
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
    url = get_single_product_url + str(product_id)
    r   = requests.get(url)
    return r.json()


def get_single_user(user_id):
    url = get_single_user_url + str(user_id)
    r   = requests.get(url)

    return r.json()

class ShoppingCart(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, auto_increment=True)
    user_id       = db.Column('user_id', db.Integer)
    username      = db.Column('username', db.String)

    product_id    = db.Column('product_id', db.Integer)
    product_title = db.Column('product_title', db.String)
    product_desc  = db.Column('product_desc', db.String)
    product_price = db.Column('product_price', db.Integer)

    quantity      = db.Column('quantity', db.Integer)
    auto_date     = db.Column('auto_date', db.DateTime, default=datetime.datetime.now)

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



class HandleShoppingCart(Resource):
    
    @marshal_with(shopping_cart_fields)
    def get(self, user_id: int):
        # Return the entire shopping cart of a specific user
        data = ShoppingCart.query.filter_by(user_id=user_id).all()
        return data


    def delete(self, user_id: int):
        # Delete the entire shopping cart of a specific user
        shopping_cart_to_delete = ShoppingCart.query.filter_by(user_id=user_id)

        if shopping_cart_to_delete.first() == None:
            return make_response(f"Shopping cart of user {user_id} does not exist!", 404)
        else:
            print(shopping_cart_to_delete)
            shopping_cart_to_delete.delete()
            db.session.commit()

        return make_response(f"Shopping cart of user {user_id} has been deleted!", 204)



class HandleProduct(Resource):
    @marshal_with(shopping_cart_fields)
    def post(self, user_id: int, product_id: int):
        # Add a specific product to a specific user's shopping cart
        pass

    @marshal_with(shopping_cart_fields)
    def delete(self, user_id: int, product_id: int):
        # Delete a specific product from a specific user's shopping cart
        pass

    @marshal_with(shopping_cart_fields)
    def put(self, user_id: int, product_id: int):
        # Change the quantity of a specific product from a specific user's shopping cart
        pass




api.add_resource(HandleShoppingCart, '/cart/<int:user_id>')
api.add_resource(HandleProduct,      '/cart/<int:user_id>/product/<int:product_id>')


if __name__ == '__main__':
    # db.destroy_all()
    db.create_all()
    app.run(debug=True)





#
# Generate fake data
# 
# @app.route('/fake')
# def FakeDataData():
#     # 145 Records generated in 300 iterations
#     for _ in range(300):
#         gen_product = get_single_product(random.randint(1, 20))
#         gen_user    = get_single_user(random.randint(1, 10))
#         quantity    = random.randint(1, 5)
        
#         # Avoid creating duplicate records instead of creating an algorithm to remove all duplicate records...
#         # Adding this one line was much easier than creating an algorithm to remove duplicate records :)
#         if db.session.query(ShoppingCart).filter_by(product_id=gen_product['id'], user_id=gen_user['id']).first() != None:
#             print(f"Duplicate detected! with {gen_product['id']}, {gen_user['id']}")
#             continue


#         new_cart = ShoppingCart(user_id=gen_user['id'], username=gen_user['username'], \
#                                 product_id=gen_product['id'], \
#                                 product_title=gen_product['title'], \
#                                 product_desc=gen_product['description'], \
#                                 product_price=gen_product['price'], quantity=quantity)
#         db.session.add(new_cart)
#         db.session.commit()
        
#         print("Cart created", new_cart)

#     return 'Done!'
