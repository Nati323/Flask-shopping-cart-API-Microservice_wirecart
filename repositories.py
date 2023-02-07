from flask_restful import marshal_with

from shopping_cart import (ModelNotFoundException, ShoppingCart, get_single_product,
                           get_single_user, shopping_cart_fields)

#
# Exceptions
#

class UserDoesNotHaveAShoppingCartException(Exception):
    """
     The user doesn't have a shopping cart
    """
    pass

class ProductAlreadyInShoppingCartException(Exception):
    """
     The user already have the item in the shopping cart but tries to add it again
    """
    pass

class InvalidQuantityException(Exception):
    """
     The user tries to enter an invalid quantity
    """
    pass




class ShoppingCartRepository():
    def __init__(self, db_session, user_id: int):
        """
         Validate the required arguments and initialize the required properties
        """

        # Make sure the user exists before continuing
        try:
            get_single_user(user_id)
        except ModelNotFoundException:
            raise ModelNotFoundException(f"User #{user_id} does not exist!", 404)

        # Make sure the user got at least 1 shopping cart instance
        if db_session.query(ShoppingCart).filter_by(user_id=user_id).first() == None:
            raise UserDoesNotHaveAShoppingCartException(f"User #{user_id} does not have any shopping carts!")

        # Make the shopping cart
        self._session       = db_session
        self._shopping_cart = self._session.query(ShoppingCart).filter_by(user_id=user_id)
        self._user_id       = user_id



    @marshal_with(shopping_cart_fields)
    def get(self):
        """
         Show user's shopping cart
        """
        return self._session.query(ShoppingCart).filter_by(user_id=self._user_id).all()


    def delete(self):
        """
         Delete user's shopping cart
        """
        product_to_delete = self._session.query(ShoppingCart).filter_by(user_id=self._user_id).first()

        self._session.delete(product_to_delete)
        self._session.commit()
        return 204







class ProductRepository():
    def __init__(self, db_session, user_id: int, product_id: int):
        """
         Validate the required arguments and initialize the required properties

         @throws ModelNotFound
        """

        # Make sure the user exists before continuing
        try:
            user = get_single_user(user_id)
        except ModelNotFoundException:
            raise ModelNotFoundException(f"User #{user_id} does not exist!")

        # Make sure the product exists before continuing
        try:
            product = get_single_product(product_id)
        except ModelNotFoundException:
            raise ModelNotFoundException(f"Product #{product_id} does not exist!")

        # Make the shopping cart
        self._session       = db_session
        self._shopping_cart = self._session.query(ShoppingCart).filter_by(user_id=user_id)
        self._user_id       = user_id
        
        self._product_id    = product_id
        self._product       = product
        self._user          = user



    @marshal_with(shopping_cart_fields)
    def add(self):
        """
         Add the product to the user's shopping cart

         @throws ProductAlreadyInShoppingCart
        """
        if self._session.query(ShoppingCart).filter_by(product_id=self._product_id, user_id=self._user_id).first() != None:
            raise ProductAlreadyInShoppingCartException(f"Product #{self._product_id} is already in user #{self._user_id}'s shopping cart!")

        new_product = ShoppingCart(
            user_id       = self._user_id,
            username      = self._user['username'],
            product_id    = self._product_id,
            product_title = self._product['title'],
            product_desc  = self._product['description'],
            product_price = self._product['price'],
            quantity      = 1
        )        

        self._session.add(new_product)
        self._session.commit()

        return new_product


    def delete(self):
        """
         Delete the product from the user's shopping cart

         @throws UserDoesNotHaveAShoppingCart
        """
        # Make sure the user got at least 1 shopping cart instance
        if self._session.query(ShoppingCart).filter_by(user_id=self._user_id).first() == None:
            raise UserDoesNotHaveAShoppingCartException(f"User #{self._user_id} does not have any shopping cart instances!")

        product_to_delete = self._session.query(ShoppingCart).filter_by(user_id=self._user_id, product_id=self._product_id).first()

        if product_to_delete == None:
            raise ModelNotFoundException(f"Product #{self._product_id} does not exist in user #{self._user_id}'s shopping cart!")

        self._session.delete(product_to_delete)
        self._session.commit()

        return 204


    def change_quantity(self, quantity: int):
        """
         Change the quantity of a specific product from a specific user's shopping cart

         @throws UserDoesNotHaveAShoppingCart
        """
        # Make sure the user got at least 1 shopping cart instance
        if self._session.query(ShoppingCart).filter_by(user_id=self._user_id).first() == None:
            raise UserDoesNotHaveAShoppingCartException(f"User #{self._user_id} does not have any shopping cart instances!")

        # Validate quantity
        if quantity < 1:
            raise InvalidQuantityException("Quantity must be greater than 0!")
        elif not isinstance(quantity, int):
            raise InvalidQuantityException("Quantity must be an integer!")
        elif quantity > 100:
            raise InvalidQuantityException("Quantity must be less than 100!")

        
        product_to_update = self._session.query(ShoppingCart).filter_by(user_id=self._user_id, product_id=self._product_id).first()

        if product_to_update == None:
            raise ModelNotFoundException(f"Product #{self._product_id} does not exist in user #{self._user_id}'s shopping cart!")


        product_to_update.quantity = quantity
        self._session.commit()

        return 200
