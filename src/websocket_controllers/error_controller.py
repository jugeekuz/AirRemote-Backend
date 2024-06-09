import json
from .mixins.websocket_mixins import WebSocketMixin
from ..models import RequestPoolModel
from .validators.error_validator import ErrorValidator
from ..utils.helpers import error_handler

class ErrorController(WebSocketMixin):
    def __init__(self, 
                 endpoint_url: str, 
                 connection_id: str,
                 request_pool_model: RequestPoolModel):
        
        self.request_pool_model = request_pool_model
        self.validator = ErrorValidator(request_pool_model)
        super().__init__(endpoint_url, connection_id)


    @WebSocketMixin.notify_if_error
    def handle_error_message(self, message: dict):
        '''
        Method that receives an error message that request with `request_id` resulted in an error and forwards the message to the client who requested it originally.
        :param dict `message`: Error message that must contain `request_id`.
        :return : Response of the attempt to send the message to the websocket connection.
        '''
        self.validator.validate_error_message(message)
        
        requestpool_response = self.request_pool_model.get_requests({'requestId': message['requestId']})

        # request = json.loads(request_response['body']['requestBody'])

        deletereq_response = self.request_pool_model.delete_request({'requestId': message['requestId']})

        error_message = {
            'action': 'error',
            'requestId': message['requestId'],
            'body': message['body']
        }

        return self.send_message(error_message, requestpool_response['body']['connectionId'])
    
    @WebSocketMixin.notify_if_error
    def route(self, request: dict):
        return self.handle_error_message(request)