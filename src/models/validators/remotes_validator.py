import re
from ..mixins.validators import BaseValidator
class RemotesValidator(BaseValidator):
    def check_mac_address(self, mac: str):

        if not isinstance(mac, str):
            return False
        
        pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

        return re.match(pattern, mac)
    
    def check_remote_name(self, remote_name: str):
        if not isinstance(remote_name, str):
            return False
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, remote_name)

    def check_command_size(self, command_size: str):
        if not isinstance(command_size, str):
            return False

        allowed_sizes = ['16', '32', '64']

        return (command_size in allowed_sizes)

    def check_protocol(self, protocol_name: str):
        if not isinstance(protocol_name, str):
            return False

        allowed_sizes = ['NAC']

        return (protocol_name in allowed_sizes)
    
    def check_buttons(self, buttons: list):
        return isinstance(buttons, list)
    
    def check_button_name(self, button_name: str):
        if not isinstance(button_name, str):
            return False
        
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, button_name)
    
    def check_button_code(self, button_code: str, command_size: str):
        if not self.check_command_size(command_size):
            return False
        
        if not isinstance(button_code, str):
            return False
        
        if button_code[0:2] != '0x':
            return False

        if int(button_code, 16).bit_length() == int(command_size):
            return False
        
        pattern = r'^[0-9A-Fa-f]+$'

        return re.match(pattern, button_code)
    
    def validate(self, items: dict):
