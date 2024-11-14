import re
import json
from datetime import datetime
from .mixins import BaseValidator

class RegisteredUsersValidator(BaseValidator):

    def check_email(self, user_email: str):

        if not isinstance(user_email, str):
            return False
        
        if re.match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', user_email) is None:
            return False
        
        return True
    
    def validate(self, items: dict, params: list):
        check_attributes = {
            'userEmail': self.check_email,
        }
        super().validate(check_attributes, items, params=params)


    