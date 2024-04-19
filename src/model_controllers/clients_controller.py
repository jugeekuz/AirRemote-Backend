from .mixins.model_handler import ObjectDynamodb
from ..websockets.websockets_handler import WebSocket

class ClientsController(ObjectDynamodb):
    '''
    Class used to handle clients.
    This class provides capability to store, retrieve, update and delete clients from AWS DynamoDB.
    '''
    def __init__(self, remote_table: str, websocket: WebSocket):
        self.websocket = websocket

        super().__init__(remote_table)
        
    def get_clients(self, send: bool = False):
        response = self.get_items()

        if send :
            _ = self.websocket.send_message(response)

        return response

    def get_client(self, client: dict, send: bool = False):
        response = self.get_item(client)

        if send :
            _ = self.websocket.send_message(response)

        return response
    
    def add_client(self, client: dict, send: bool = False):
        response = self.add_item(client)

        if send :
            _ = self.websocket.send_message(response)

        return response
    
    def delete_client(self, client: dict, send: bool = False):
        response = self.delete_item(client)

        if send :
            _ = self.websocket.send_message(response)

        return response
    
    def filter_items(self, filters: dict = None, send: bool = False):
        response = self.scan_items(filters)

        if send:
            _ = self.websocket.send_message(response)

        return response