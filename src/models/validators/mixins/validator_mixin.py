class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class BaseValidator:
    '''
    Class to be used as base class to be inherited by other validators.
    '''

    def validate(self, check_attributes: dict, items: dict, params: list=None):
        '''
        Method used to validate items using functions passed as callbacks and raise ValidationError if they fail.
        :param dict `check_attributes`: Dictionary containing attribute name as key and callback function to be used to validate it as value.
        :param dict `items`: Dictionary containing items to be checked. If the key is not present it will raise `AttributeError` if test doesn't pass then `ValidationError`.
        :param list `params`: List containing attributes that should exist in `items`, `None` if items can have different attributes.
        '''
        if params :
            if len(params)!=len(items) or not all(attr in items for attr in params):
                raise AttributeError(f"Expected attributes `{params}`, received `{list(items.keys())}`.")
           
        for key, value in items.items():
            if key not in check_attributes:
                raise AttributeError(f"Key specified `{key}` does not exist.")
            if not check_attributes[key](value):
                raise ValidationError(f"Invalid format for `{key}`, received `{value}`.")

