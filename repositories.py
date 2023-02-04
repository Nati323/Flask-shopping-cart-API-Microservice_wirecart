from flask import make_response
from flask_restful import marshal_with
from shopping_cart import ShoppingCart, get_single_product, get_single_user, shopping_cart_fields

#
# Exceptions
#
class ModelNotFound(Exception):
    "Raised when the modal isn't found in the database or isn't found in the external API"
    pass

class UserDoesNotHaveAShoppingCart(Exception):
    "Raised when the user doesn't have a shopping cart"
    pass




class ShoppingCartRepository():
    def __init__(self, db_session, user_id: int):

        # Make sure the user exists before continuing
        try:
            get_single_user(user_id)
        except ModelNotFound:
            return make_response(f"User #{user_id} does not exist!", 404)

        # Make sure the user got at least 1 shopping cart
        if db_session.query(ShoppingCart).filter_by(user_id=user_id).first() == None:
            raise UserDoesNotHaveAShoppingCart(f"User #{user_id} does not have any shopping carts!")

        # Make the shopping cart
        self._session       = db_session
        self._shopping_cart = self._session.query(ShoppingCart).filter_by(user_id=user_id)
        self._user_id       = user_id



    @marshal_with(shopping_cart_fields)
    def get(self):
        return self._session.query(ShoppingCart).all()


    def delete(self):
            product_to_delete = self._session.query(ShoppingCart).filter_by(user_id=self._user_id).first()

            self._session.delete(product_to_delete)
            self._session.commit()
            return 204







class ProductRepository():
    def __init__(self, db_session, user_id: int, product_id: int):

        # Make sure the user exists before continuing
        try:
            get_single_user(user_id)
        except ModelNotFound:
            return make_response(f"User #{user_id} does not exist!", 404)

        # Make sure the product exists before continuing
        try:
            get_single_product(product_id)
        except ModelNotFound:
            return make_response(f"Product #{product_id} does not exist!", 404)

        # Make sure the user got at least 1 shopping cart
        if db_session.query(ShoppingCart).filter_by(user_id=user_id).first() == None:
            raise UserDoesNotHaveAShoppingCart(f"User #{user_id} does not have any shopping carts!")

        # Make the shopping cart
        self._session       = db_session
        self._shopping_cart = self._session.query(ShoppingCart).filter_by(user_id=user_id)
        self._user_id       = user_id
        self._product_id    = product_id



    def add(self):
        pass


    def delete(self):
        pass


    def change_quantity(self):
        pass