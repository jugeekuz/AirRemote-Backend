import json
from .mixins.websocket_mixins import WebSocketMixin
from ..models import RequestPoolModel
from ..utils.helpers import error_handler

class ACKController(WebSocketMixin):
    def __init__(self, 
                 endpoint_url: str, 
                 connection_id: str,
                 request_pool_model: RequestPoolModel):
        
        self.request_pool_model = request_pool_model

        super().__init__(endpoint_url, connection_id)


    @error_handler
    def handle_ack_message(self, message: dict):    
        '''
        Method that receives an acknowledgment message that request with `request_id` was carried out successfully and forwards the message to the client who requested it originally.
        :param dict `message`: Acknowledgement message that must contain `request_id`.
        :return : Response of the attempt to send the message to the websocket connection.
        '''

        request_response = self.request_pool_model.get_requests({'requestId': message['requestId']})

        request = json.loads(request_response['body'])

        request_response = self.request_pool_model.delete_request({'requestId': request['requestId']})

        ack_message = {
            'action': 'msg',
            'type': 'ack',
            'requestId': request['body']['requestId'],
            'body': 'success'
        }

        return self.send_message(ack_message, request['connectionId'])
    
    @error_handler
    def route(self, request: dict):
        return self.handle_ack_message(request)