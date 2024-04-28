class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class BaseValidator:
    '''
    Class to be used as base class to be inherited by other validators.
    '''

    def validate(self, check_attributes: dict, items: dict):
        '''
        Method used to validate items using functions passed as callbacks and raise ValidationError if they fail.
        :param dict `check_attributes`: Dictionary containing attribute name as key and callback function to be used to validate it as value.
        :param dict `items`: Dictionary containing items to be checked. If the key is not present it will raise `AttributeError` if test doesn't pass then `ValidationError`.
        '''
        for key, value in items.items():
            if key not in check_attributes:
                raise AttributeError(f"Key specified `{key}` does not exist.")
            if not check_attributes[key](value):
                raise ValidationError(f"Invalid format for `{key}`, received `{value}`.")




def type_checker(item: dict, keys: list):
    for (key, data_type) in keys:
        if not key in item:
            raise AttributeError
        if not type(item[key]) is data_type:
            raise AttributeError
 

class DeviceValidators:
    def mac_checker(item: str):
        pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

        return re.match(pattern, item)

    def device_type_checker(item: str):
        allowed_devices = ['iot', None]

        return item in allowed_devices

    def device_name_checker(item: str):
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, item)
    
    def check():
        pass


#Remote validators
class RemoteValidators:
    def remote_name_checker(item: str):
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, item)

    def command_size_checker(item: str):
        allowed_command_sizes = ['16', '32', '64', '128']

        return item in allowed_command_sizes

def is_valid(item: dict, type: str):
    allowed_types = ['MAC']
    if not type in allowed_types:
        raise AttributeError
    
    if type == 'MAC':
