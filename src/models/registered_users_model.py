import re
from .mixins import ObjectDynamodb
from .validators import RegisteredUsersValidator
from ..utils.helpers import error_handler, check_response
from ..utils.errors import ResponseError

class RegisteredUsersModel(ObjectDynamodb):
    def __init__(self, users_table: str):

        self.validator = RegisteredUsersValidator()

        super().__init__(users_table)
        
 
    @error_handler
    def get_user(self, user: dict = None):
        if user:
            
            self.validator.validate(user, params=['userEmail'])

            return self.get_item(user)
        else:

            return self.scan_items()

    @error_handler
    def add_user(self, user: dict):

        self.validator.validate(user, params=['userEmail'])
        
        return self.add_item(user)


    @error_handler
    def delete_remote(self, user: dict):
        
        self.validator.validate(user, params=['userEmail'])

        response = self.delete_item(user)

        return response