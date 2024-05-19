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
        if not isinstance(key, str):
            return False

        if len(key)%4 != 0:
            return False
        
        if not re.match(r'^[A-Za-z0-9+/\-]+={0,2}$', key):
            return False
        
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
    
    def validate(self, items: dict, params: list):
        check_attributes = {
            'deviceType': self.check_device_type,
            'deviceName': self.check_device_name,
            'macAddress': self.check_mac,
            'connectionId': self.check_connection_id
        }
        super().validate(check_attributes, items, params=params)