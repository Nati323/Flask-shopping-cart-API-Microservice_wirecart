import datetime
import time
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, fields, marshal_with
from flask import Flask, Response, make_response, request
import requests
import random

app = Flask(__name__)
api = Api(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_cart_db.sqlite3' # db.sqlite3 is the database name, aka. file name
app.app_context().push()
db = SQLAlchemy(app)


#
# Exceptions
#
class ModelNotFound(Exception):
    "Raised when the modal isn't found in the database or isn't found in the external API"
    pass



# API URLs
get_single_user_url    = 'https://fakestoreapi.com/users/'
get_single_product_url = 'https://fakestoreapi.com/products/'


def get_single_product(product_id):
    url = get_single_product_url + str(product_id)
    r   = requests.get(url)

    if r.content == b'' or r.content == 'null':
        raise ModelNotFound(f"Product #{product_id} does not exist!")
    
    return r.json()



def get_single_user(user_id):
    url = get_single_user_url + str(user_id)
    r   = requests.get(url)

    if r.content == b'' or r.content == 'null':
        raise ModelNotFound(f"User #{user_id} does not exist!")

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
        """
        Return the entire shopping cart of a specific user
        """
        data = ShoppingCart.query.filter_by(user_id=user_id).all()
        return data


    def delete(self, user_id: int):
        """
         Delete the entire shopping cart of a specific user
        """
        shopping_cart_to_delete = ShoppingCart.query.filter_by(user_id=user_id)

        if shopping_cart_to_delete.first() == None:
            return make_response(f"Shopping cart of user #{user_id} does not exist!", 404)
        else:
            print(shopping_cart_to_delete)
            shopping_cart_to_delete.delete()
            db.session.commit()

        return make_response(f"Shopping cart of user #{user_id} has been deleted!", 204)



class HandleProduct(Resource):
    def post(self, user_id: int, product_id: int):
        """
         Add a specific product to a specific user's shopping cart
        """
        #
        # Validations
        # Check if the product, user exist, and check if the product is already in the user's shopping cart
        #
        try:
            product = get_single_product(product_id)        
        except ModelNotFound:
            return make_response(f"Product #{product_id} does not exist!", 404)

        try:
            user = get_single_user(user_id)
        except ModelNotFound:
            return make_response(f"User #{user_id} does not exist!", 404)


        # Check if the product is already in the user's shopping cart
        if db.session.query(ShoppingCart).filter_by(product_id=product_id, user_id=user_id).first() != None:
            return make_response(f"Product #{product_id} is already in user #{user_id}'s shopping cart! Try changing the quantity instead.", 400)


        # Add the product to the user's shopping cart
        new_product = ShoppingCart(
            user_id       = user_id,
            username      = user['username'],
            product_id    = product_id,
            product_title = product['title'],
            product_desc  = product['description'],
            product_price = product['price'],
            quantity      = 1
        )

        db.session.add(new_product)
        db.session.commit()

        return make_response(f"Product #{product_id} has been added to user #{user_id}'s shopping cart!", 201)


    def delete(self, user_id: int, product_id: int):
        """
         Delete a specific product from a specific user's shopping cart\
        """
        product_to_delete = ShoppingCart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if product_to_delete == None:
            return make_response(f"Product #{product_id} does not exist in user #{user_id}'s shopping cart!", 404)
        
        db.session.delete(product_to_delete)
        db.session.commit()

        return make_response(f"Product #{product_id} has been deleted from user #{user_id}'s shopping cart!", 204)
    

    def put(self, user_id: int, product_id: int):
        """
         Change the quantity of a specific product from a specific user's shopping cart
        """
        product_to_update = ShoppingCart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if product_to_update == None:
            return make_response(f"Product #{product_id} does not exist in user #{user_id}'s shopping cart!", 404)
        
        product_to_update.quantity = request.json['quantity']
        db.session.commit()

        return make_response(f"Product #{product_id} has been updated in user #{user_id}'s shopping cart!", 200)





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
