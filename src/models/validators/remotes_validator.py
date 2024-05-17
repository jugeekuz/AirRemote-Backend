import re
from typing import Tuple
from .mixins import BaseValidator

class RemotesValidator(BaseValidator):
    def check_mac(self, mac: str):
        '''
        Method that checks if given argument is str and valid MAC address
        '''
        if not isinstance(mac, str):
            return False
        
        pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

        return re.match(pattern, mac)
    
    def check_remote_name(self, remote_name: str):
        '''
        Method that checks if given argument is str and valid remote name
        '''
        if not isinstance(remote_name, str):
            return False
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, remote_name)

    def check_command_size(self, command_size: str):
        '''
        Method that checks if given argument is str and valid supported command size
        '''
        if not isinstance(command_size, str):
            return False

        allowed_sizes = ['16', '32', '64']

        return (command_size in allowed_sizes)

    def check_protocol(self, protocol_name: str):
        '''
        Method that checks if given argument is str and valid and supported protocol name
        '''
        if not isinstance(protocol_name, str):
            return False

        allowed_sizes = ['NAC']

        return (protocol_name in allowed_sizes)
    
    def check_button_name(self, button_name: str):
        '''
        Method that checks if given argument is str and valid button name
        '''
        if not isinstance(button_name, str):
            return False
        
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, button_name)
    
    def check_button_code(self, button_size_tuple: Tuple[str, str]):
        '''
        Method that checks if given argument button code is valid hex code and of bit length command size
        '''
        (button_code, command_size) = button_size_tuple
        
        if not isinstance(button_code, str):
            return False
        
        if button_code[0:2] != '0x':
            return False
        
        pattern = r'^[0-9A-Fa-f]+$'

        if not re.match(pattern, button_code[2:]):
            return False

        return (int(button_code, 16).bit_length() == int(command_size))


    
    def validate(self, items: dict, params: list):
        check_attributes = {
            'remoteName': self.check_remote_name,
            'protocol': self.check_protocol,
            'macAddress': self.check_mac,
            'commandSize': self.check_command_size,
            'buttons': self.check_buttons,
            'buttonName': self.check_button_name,
            'buttonCode': self.check_button_code
        }
        super().validate(check_attributes, items, params=params)