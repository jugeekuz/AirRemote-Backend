from .mixins.model_handler import ObjectDynamodb
from ..websockets.websockets_handler import WebSocket

class RemoteController(ObjectDynamodb):
    '''
    Class used to handle remote control commands.
    This class provides capability to store, retrieve, update and delete remotes from AWS DynamoDB.
    '''
    def __init__(self, remote_table: str, websocket: WebSocket):
        self.websocket = websocket

        super().__init__(remote_table)
        
    def get_remotes(self, send: bool = False):
        response = self.get_items()
        if send :
            _ = self.websocket.send_message(response)
        return response

    def get_remote(self, remote: dict, send: bool = False):
        response = self.get_item(remote)
        if send :
            _ = self.websocket.send_message(response)
        return response

    def add_remote(self, remote: dict, send: bool = False):
        response = self.add_item(remote)
        if send :
            _ = self.websocket.send_message(response)
        return response

    def add_button(self, remote: dict, button: dict, send: bool = False):
        response = self.append_to_list(remote, "buttons", button)
        if send :
            _ = self.websocket.send_message(response)
        return response
    
    def delete_remote(self, remote: dict, send: bool = False):
        response = self.delete_item(remote)
        if send :
            _ = self.websocket.send_message(response)
        return response
    
    def send_command_button(self, mac_address: str, remote_name: str, button_name: str, send: bool = False):
        raise NotImplementedError
    
    def request_button_code(self, mac_address: str, remote_name: str, button_name: str, send: bool = False):
        raise NotImplementedError
    
    def register_button_code(self, mac_address: str, button_name: str, button_code: str, send: bool = False):
        raise NotImplementedError


    