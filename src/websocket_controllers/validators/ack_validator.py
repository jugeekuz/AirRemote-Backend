import json
import re
from ...models import RequestPoolModel, RemotesModel
from .mixins.validator_mixin import BaseRequestValidator
from ...utils.errors import InvalidRequestError

class ACKValidator(BaseRequestValidator):
    def __init__(self, requestpool_model: RequestPoolModel, remotes_model: RemotesModel):
        self.requestpool_model = requestpool_model
        self.remotes_model = remotes_model
        super().__init__()

    def validate_ack_read(self, request: dict):

        allowed_attributes = ["action", "requestId", "buttonCode"]

        self.check_request(request, allowed_attributes)

        requestpool_response = self.requestpool_model.get_requests({"requestId": request["requestId"]})

        if requestpool_response['statusCode']==404 or requestpool_response['statusCode']==500:
            raise InvalidRequestError('RequestId does not exist.')

        req = requestpool_response['body']
        try: 
            orig_request = json.loads(req['requestBody'])
        except:
            raise InvalidRequestError('Unexpected issue with loading original request.')
        
        remotes_response = self.remotes_model.get_remotes({"remoteName": orig_request["remoteName"]})
        if remotes_response['statusCode']==404 or remotes_response['statusCode']==500:
            raise InvalidRequestError('Remote no longer exists.')
        command_size = remotes_response['body']['commandSize']

        #Check if button code is valid HEX code
        pattern = r'^[0-9A-Fa-f]+$'

        if request['buttonCode'][0:2] != '0x' or not re.match(pattern, request['buttonCode'][2:]):
            raise InvalidRequestError("Code provided is not valid hex code.")
        
        #Check if bit length of provided buttonCode matches the requested one
        if int(request['buttonCode'], 16).bit_length() != int(command_size):
            raise InvalidRequestError(f"Code bit length provided doesn't match the requested one of {command_size} bits")
        


    def validate_ack_execute(self, request: dict):

        allowed_attributes = ["action", "requestId", "buttonCode"]

        self.check_request(request, allowed_attributes)

        requestpool_response = self.requestpool_model.get_requests({"requestId": request["requestId"]})

        if requestpool_response['statusCode']==404 or requestpool_response['statusCode']==500:
            raise InvalidRequestError('RequestId does not exist.')

        orig_request = requestpool_response['body']
        try: 
            orig_request = json.loads(orig_request)
        except:
            raise InvalidRequestError('Unexpected issue with loading original request.')
        
       
        


        