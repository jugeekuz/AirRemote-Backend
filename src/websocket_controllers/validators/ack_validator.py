import json
import ast
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

        allowed_attributes = ["action", "requestId", "buttonCode", "commandSize"]

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

        #Check if button code is valid 

        try:
            raw_list = ast.literal_eval(request['buttonCode'])
        except:
            raise InvalidRequestError("Code provided is not valid code in raw format.")
        
        for item in raw_list:
            if not isinstance(item, int):
                raise InvalidRequestError
            
        if len(raw_list) != int(request['commandSize']):
            raise InvalidRequestError(f"Code bit length provided doesn't match the requested one of {request['commandSize']} bits")
            
        
       


    def validate_ack_execute(self, request: dict):

        allowed_attributes = ["action", "requestId"]

        self.check_request(request, allowed_attributes)

        requestpool_response = self.requestpool_model.get_requests({"requestId": request["requestId"]})

        if requestpool_response['statusCode']==404 or requestpool_response['statusCode']==500:
            raise InvalidRequestError('RequestId does not exist.')

        req = requestpool_response['body']
        try: 
            orig_request = json.loads(req['requestBody'])
        except:
            raise InvalidRequestError('Unexpected issue with loading original request.')
        
       
        


        