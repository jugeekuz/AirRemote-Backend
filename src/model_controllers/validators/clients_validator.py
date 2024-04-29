import re
from .mixins.validators import BaseValidator

class ClientsValidator(BaseValidator):

    def check_connection_id(self, key: str):
        '''
        Checks if `key` is in valid format by being `str` and in Base64 format.
        '''
        if not isinstance(key, str):
            return False

        if len(key)%4 != 0:
            return False
        
        return re.match(r'^[A-Za-z0-9+/]+={0,2}$', key)
    
    def check_device_type(self, device: str):
        '''
        Method that checks if device type is valid and allowed.
        '''
        if not isinstance(device, str):
            return False

        allowed_types = ['iot', None]

        return (device in allowed_types)
    
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
            