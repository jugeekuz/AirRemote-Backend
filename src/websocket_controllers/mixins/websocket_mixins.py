import json
import boto3
from ...utils.helpers import error_handler, check_response
from ...models import DevicesModel
import functools

class WebSocketMixin:
    '''
    Class meant to handle connections and operations regarding WebSocket connections (such as sending messages).
    '''
    def __init__(self, 
                 endpoint_url: str, 
                 connection_id: str,):
        '''
        :param str `endpoint_url`: String containing the url of the websocket gateway endpoint.
        :param str `connection_id`: The connection id of this connection sending the request.
        '''
        self.api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
        self.connection_id = connection_id

    
    
    @error_handler
    def send_message(self, body: dict, connection_id: str = None):
        '''
        Method sending `body` through api_gateway to given `connection_id`.

        :param dict `body`: Message to send.
        :return : Response 200 or error.
        '''
        response = self.api_gateway.post_to_connection(
            Data = json.dumps(body),
            ConnectionId = self.connection_id if not connection_id else connection_id
        )
        return {"statusCode": 200,
                "body": "OK"}
    
    
    @error_handler
    def send_broadcast(self, body: dict, clients: list):
        '''
        Method sending `body` to all connections contained in `response`, except `self.connection_id`.

        :param dict `body`: Message to send.
        :param list `clients` : List of clients to send message to.
        :return: Response 200 or error.
        '''
        for item in clients:
            if item["connectionId"] != self.connection_id:
                _ = self.send_message(body, item["connectionId"])

        return {"statusCode": 200,
                "body": "OK"}
    
    @staticmethod
    def notify_if_error(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                error_message = {
                    "action": "error",
                    "body": f"{str(e)}"
                }
                self.send_message(error_message)
                
                return {"statusCode": 500,
                        "body": f"Received unexpected error in `{func.__name__}` : {e}"}
        return wrapper
    
    
    
class WebSocketMixinV2(WebSocketMixin):
    def __init__(self, 
                 endpoint_url: str, 
                 connection_id: str,
                 devices_model: DevicesModel):
        '''
        :param str `endpoint_url`: String containing the url of the websocket gateway endpoint.
        :param str `connection_id`: The connection id of this connection sending the request.
        '''

        self.devices_model = devices_model

        super().__init__(endpoint_url, connection_id)
   

    def _send_message_device(self, mac_address: dict, message: dict):
        '''
        Method used to send message to a device by its' MAC address (if the device is connected).

        :param dict `mac_address`: Dictionary containing key-value pair `macAddress` and the mac_address of the device.
        :return : Response of the send command or error.
        '''

        device = self.devices_model.get_devices(mac_address)

        if check_response(device) and device["body"]['connectionId']:
            return self.send_message(message, device["body"]['connectionId'])
        
        return {"statusCode": 500,
                "body": f"Device with MAC address {mac_address["macAddress"]} is not connected or doesn't exist."}
    
    
    
