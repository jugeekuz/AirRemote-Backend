import re
from .mixins import BaseValidator

class ClientsValidator(BaseValidator):

    def check_connection_id(self, key: str):
        '''
        Checks if `key` is in valid format by being `str` and in Base64 format.
        '''
        if not isinstance(key, str):
            return False
        
        return True
    
    def check_device_type(self, device: str):
        '''
        Method that checks if device type is valid and allowed.
        '''
        if not isinstance(device, str):
            return False

        allowed_types = ['iot', 'client', None]

        return (device in allowed_types)
    
    def check_salt(self, salt: str):
        if not isinstance(salt, str):
            return False

        return True
    
    def check_auth_token(self, token: str):
        if not isinstance(token, str):
            return False

        return True
    
    def validate(self, items: dict, params: list=None):
        '''
        Method used to validate types and values of items.
        :param dict `items`: Dictionary containing keys as attribute names and values to be checked.
        '''
        check_attributes = {
            'connectionId': self.check_connection_id, 
            'deviceType': self.check_device_type
        }
        super().validate(check_attributes, items, params=params)
            