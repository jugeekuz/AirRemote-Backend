import time
import json
import boto3
from ..model_controllers.clients_controller import ClientsController
from ..utils.helpers import error_handler, check_response
class WebSocket:
    '''
    Class meant to handle connections and operations regarding WebSocket connections.
    This class offers the ability to handle connections, disconnections, sending messages and more.
    '''
    def __init__(self, endpoint_url: str, connection_id: str, clients_model: ClientsController):
        '''
        :param `api_gateway`: boto3 `apigatewaymanagementapi` resource.
        :param str `connection_id`: The connection id of this connection sending the request.
        :param ObjectDynamodb `clients_model`: Object of the table regarding client connections.
        :param ObjectDynamodb `devices`: Object of the table regarding connected and registered devices.
        '''
        self.api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
        self.connection_id = connection_id
        self.clients_model = clients_model
    
    @error_handler
    def send_message(self, body: dict, connection_id: str = None):
        '''
        Method sending `body` through api_gateway to given `connection_id`.

        :param `body`: Message to send.
        :return : Response 200 or error.
        '''
        response = self.api_gateway.post_to_connection(
            Data = json.dumps(body),
            ConnectionId = self.connection_id if not connection_id else connection_id
        )
        return {"statusCode": 200,
                "body": "OK"}
    
    @error_handler
    def send_broadcast(self, body: dict):
        '''
        Method sending `body` to all connections, except `this_connection_id`.

        :param `this_connection_id`: Connection Id sending the message.
        :param `body`: Message to send.
        :return: Response 200 or error.
        '''
        response = self.clients_model.get_clients()

        if response["statusCode"] == 200:
            for item in response['body']:
                if item["connectionId"]['S'] != self.connection_id:
                    _ = self.send_message(body, item["connectionId"])

        return {"statusCode": 200,
                "body": "OK"}

