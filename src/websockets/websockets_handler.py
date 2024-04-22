import time
import json
import boto3
from ..utils.helpers import error_handler, check_response

class WebSocket:
    '''
    Class meant to handle connections and operations regarding WebSocket connections.
    This class offers the ability to handle connections, disconnections, sending messages and more.
    '''
    def __init__(self, endpoint_url: str, connection_id: str):
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

