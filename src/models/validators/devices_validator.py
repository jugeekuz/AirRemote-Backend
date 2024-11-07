import re
from .mixins import BaseValidator

class DevicesValidator(BaseValidator):
    def check_mac(self, item: str):
        '''
        Method that checks whether item is str and valid MAC address
        '''
        if not isinstance(item, str):
            return False
        
        pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

        return re.match(pattern, item)
    
    def check_connection_id(self, key: str):
        '''
        Checks if `key` is in valid format by being `str` and in Base64 format.
        '''
        if not isinstance(key, str) and not key is None:
            return False

        # if len(key)%4 != 0:
        #     return False
        
        # if not re.match(r'^[A-Za-z0-9+/\-]+={0,2}$', key):
        #     return False
        
        return True
    

    def check_device_type(self, item: str):
        '''
        Method that checks whether item is str and valid MAC address
        '''
        if not isinstance(item, str):
            return False

        allowed_devices = ['iot', None]

        return (item in allowed_devices)
    
    def check_device_name(self, item: str):
        if not isinstance(item, str):
            return False

        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, item)
    
    def check_salt(self, salt: str):
        if not isinstance(salt, str):
            return False

        # if len(salt) != 16:
        #     return False
        
        return True
    
    def check_hash_token(self, hash_token: str):
        if not isinstance(hash_token, str):
            return False
        
        # if len(hash_token) != 16:
        #     return False
        
        return True
    def check_order_index(self, order_index: str):
        if not isinstance(order_index, str):
            return False
        
        try:
           if int(order_index) < 0:
               return False
        except:
            return False
        
        return True
    
    def validate(self, items: dict, params: list):
        check_attributes = {
            'deviceType': self.check_device_type,
            'deviceName': self.check_device_name,
            'salt': self.check_salt,
            'hashToken': self.check_hash_token,
            'macAddress': self.check_mac,
            'connectionId': self.check_connection_id,
            'orderIndex': self.check_order_index
        }
        super().validate(check_attributes, items, params=params)