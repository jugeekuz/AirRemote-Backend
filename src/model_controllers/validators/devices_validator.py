import re
from .mixins.validators import BaseValidator

class DevicesValidator(BaseValidator):
    def check_mac(self, item: str):
        '''
        Method that checks whether item is str and valid MAC address
        '''
        if not isinstance(item, str):
            return False
        
        pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

        return re.match(pattern, item)
    
    def check_device_type(item: str):
        '''
        Method that checks whether item is str and valid MAC address
        '''
        if not isinstance(item, str):
            return False

        allowed_devices = ['iot', None]

        return (item in allowed_devices)
    
    def check_device_name(item: str):
        if not isinstance(item, str):
            return False

        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, item)
    
    def validate(self, items: dict, params: list):
        check_attributes = {
            'deviceType': self.check_device_type,
            'deviceName': self.check_device_name,
            'macAddress': self.check_mac
        }
        super().validate(check_attributes, params, items)