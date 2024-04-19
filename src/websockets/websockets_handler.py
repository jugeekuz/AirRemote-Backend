import time
import json
from ..models.model_handler import ObjectDynamodb
from ..utils.helpers import error_handler, check_response
class WebSocket:
    '''
    Class meant to handle connections and operations regarding WebSocket connections.
    This class offers the ability to handle connections, disconnections, sending messages and more.
    '''
    def __init__(self, api_gateway, clients_model: ObjectDynamodb, devices_model: ObjectDynamodb):
        '''
        :param `api_gateway`: boto3 `apigatewaymanagementapi` resource.
        :param ObjectDynamodb `clients_model`: Object of the table regarding client connections.
        :param ObjectDynamodb `devices`: Object of the table regarding connected and registered devices.
        '''
        self.api_gateway = api_gateway
        self.clients_model = clients_model
        self.devices_model = devices_model
    
    @error_handler
    def send_message(self, connection_id: str, body: dict):
        '''
        Method sending `body` through api_gateway to given `connection_id`.

        :param `connection_id`: Connection Id to send the message.
        :param `body`: Message to send.
        :return : Response 200 or error.
        '''
        response = self.api_gateway.post_to_connection(
            Data = json.dumps(body),
            ConnectionId = connection_id
        )
        return {"statusCode": 200,
                "body": "OK"}
    
    @error_handler
    def send_broadcast(self, this_connection_id: str, body: dict):
        '''
        Method sending `body` to all connections, except `this_connection_id`.

        :param `this_connection_id`: Connection Id sending the message.
        :param `body`: Message to send.
        :return: Response 200 or error.
        '''
        response = self.clients_model.get_items()

        if response["statusCode"] == 200:
            for item in response['body']:
                if item["connectionId"]['S'] != this_connection_id:
                    _ = self.send_message(item["connectionId"]['S'], body)

        return {"statusCode": 200,
                "body": "OK"}


    @error_handler
    def handle_connect(self, connection_id: str):
        '''
        Method saving the given `connection_id` to `self.clients_model`.

        :param `connection_id`: Connection Id to save to Dynamo DB table
        :return: Response 200 or error. 
        '''
        connection_item = {"connectionId": connection_id,
                           "deviceType": None}
        
        response_db = self.clients_model.add_item(connection_item)

        return response_db


    @error_handler   
    def handle_disconnect(self, connection_id: str):
        '''
        Method deleting the given `connection_id` from `self.clients_table`,
        as well as deleting the connection from `self.devices_table` if it is an iot device.

        :param `connection_id`: Connection Id to remove from Dynamo DB table
        :return: 200 response to send or Error 
        '''
        connection = {
            "connectionId": connection_id
            }
        response_connection = self.clients_model.get_item(connection)
        response_clients = self.clients_model.delete_item(connection)

        if check_response(response_connection) and response_connection["body"]["deviceType"] == "iot":
           response_device = self.devices_model.scan_items(connection)

           if check_response(response_device):
               device = response_device["body"][0]
               mac_address = {
                   "macAddress": device["macAddress"]
               }
               response_device_2 = self.devices_model.update_item(mac_address, {"connectionId": None})

        return response_clients
    
    @error_handler
    def handle_device_type(self, connection_id: str, body: dict):
        '''
        Method used to handle messages from devices declaring their device type and their MAC address potentially.

        The dict `body` should contain key-value pairs in one of two formats:
        {
            "deviceType": "iot",
            "macAddress": "00-B0-D0-63-C2-26"
        }
        - OR -
        {
            "deviceType": "someOtherType"
        }

        :param str `connection_id`: The connection ID of the connection we received message from.
        :param dict `body`: The body of the request sent to API Gateway
        :return : Response 201 or Response 500
        '''
        connection = {
            "connectionId": connection_id
            }
        device_type = {
            "deviceType": body["deviceType"]
            }
        
        response_1 = self.clients_model.update_item(connection, device_type)

        if check_response(response_1) and body["deviceType"] == "iot":
            mac_address = {
                "macAddress": body["macAddress"]
                }
            #If the device is already registered then update its' connection id
            if check_response(self.devices_model.get_item(mac_address)):

                response_2 = self.devices_model.update_item(mac_address, connection)
            else:
                response_2 = self.devices_model.add_item(item={
                    **mac_address,
                    **connection,
                    "deviceName": None,
                })
                
        return response_1
        
    