from .....utils.errors import InvalidRequestError
class BaseRequestValidator:
    '''
    Class to be used as base class to be inherited by other validators.
    '''

    def check_request(self, request: dict, allowed_attributes: list):

        if not all(isinstance(attr, str) for attr in request):
            raise InvalidRequestError("Request not allowed.")
                
        if not (all(attr in allowed_attributes for attr in request) and (len(allowed_attributes) == len(request))):
            raise InvalidRequestError("Request not allowed.")  

            

