import json
from ..controllers.clients_controller import WebsocketClients
class WebSocket:
    '''
    Class meant to handle WebSocket connections
    '''
    def __init__(self, api_gateway, clients_model: WebsocketClients):
        self.api_gateway = api_gateway
        self.clients_model = clients_model
    
    def handle_connect(self, connection_id: str):
        '''
        Method saving the given `connection_id` to the specified table.
        :param connection_id: Connection Id to save to Dynamo DB table
        :return: 200 response to send or Error 
        '''

        connection_item = {"connectionId": connection_id,
                           "deviceType": None}
        
        response_db = self.clients_model.add_item(connection_item)

        request_message = {"type": "cmd",
                           "action": "requestDeviceType"}
        
        response_gateway = self.send_message(connection_id, request_message)
        return response_db
    
    def handle_disconnect(self, connection_id: str):
        '''
        Method deleting the given `connection_id` from the specified table.
        :param connection_id: Connection Id to remove from Dynamo DB table
        :return: 200 response to send or Error 
        '''
        device_type = self.clients_model.get_item({"connectionId": connection_id})["body"]["deviceType"]
        if device_type == "iot":
            pass

        return self.clients_model.delete_item(connection_id)

    def handle_device_type(self, connection_id: str, body: dict):
        dev_type = body["deviceType"]
        new_connection_item = {"connectionId": connection_id,
                               "deviceType": dev_type}
        self.clients_model.add_item(new_connection_item)
        if dev_type == "iot":
            
            self.body["macAddress"]

    def send_message(self, connection_id: str, body: dict):
        '''
        Method sending `body` through api_gateway to given `connection_id`.
        :param connection_id: Connection Id to send the message
        :param body: Message to send
        '''
        try:
            response = self.api_gateway.post_to_connection(
                Data = json.dumps(body),
                ConnectionId = connection_id
            )
            return {"statusCode": 200,
                    "body": "OK"}
        
        except Exception as e:
            return {"statusCode": 500,
                    "body": f"Received unexpected error: {e}"}
        
    def send_broadcast(self, this_connection_id: str, body: dict):
        '''
        Method sending `body` to all connections, except `this_connection_id`.
        :param this_connection_id: Connection Id sending the message
        :param body: Message to send
        :return: 200 response code or error
        '''
        try:
            response = self.clients_model.get_items()

            if response["statusCode"] == 200:
                for item in response['body']:
                    if item["connectionId"]['S'] != this_connection_id:
                        self.send_message(item["connectionId"]['S'], body)

            return {"statusCode": 200,
                    "body": "OK"}
        
        except Exception as e:
            return {"statusCode": 500,
                    "body": f"Received unexpected error: {e}"}