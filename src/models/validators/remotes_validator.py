import re
import ast
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

        try:
            command_size_int = int(command_size)
        except:
            return False
        
        if command_size_int > 1024:
            return False

        return True

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
        
        try:
            raw_list = ast.literal_eval(button_code)
        except:
            return False
        
        for item in raw_list:
            if not isinstance(item, int):
                return False
            
        if len(raw_list) != int(command_size):
            return False

        return True

    def check_button_state(self, state: str):
        
        if not isinstance(state, str):
            return False
        
        if state not in ["YES", "NO"]:
            return False
        
        return True

    def check_buttons(self, buttons: list):
        '''
        Method that checks if list of buttons is valid.
        '''
        if not isinstance(buttons, list):
            return False
        
        try:
            for btn in buttons:
                temp_btn = btn.copy()
                temp_btn['buttonCode'] = (temp_btn['buttonCode'], temp_btn['commandSize'])
                self.validate(btn, ['buttonName', 'buttonCode', 'commandSize'])
        except:
            return False
        
        return True
    
    def check_button_clicks(self, button_clicks: str):
        if not isinstance(button_clicks, str):
            return False
        
        try:
            if int(button_clicks) < 0:
                return False
        except:
            return False
        
        return True
    
    def check_remote_category(self, remote_category: str):
        if not isinstance(remote_category, str):
            return False
        allowed_values = ["Air Conditioner", "Audio System", "Dehumidifier", "Heater", "RGB Lights", "Smart TV", "Generic Device"]
        if remote_category not in allowed_values:
            return False
        return True
    
    def validate(self, items: dict, params: list):
        check_attributes = {
            'remoteName': self.check_remote_name,
            #'protocol': self.check_protocol,
            'category': self.check_remote_category,
            'macAddress': self.check_mac,
            'commandSize': self.check_command_size,
            'buttons': self.check_buttons,
            'buttonName': self.check_button_name,
            'buttonCode': self.check_button_code,
            'buttonClicks': self.check_button_clicks,
            'buttonState': self.check_button_state
        }
        super().validate(check_attributes, items, params=params)