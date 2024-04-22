from .mixins.model_handler import ObjectDynamodb
from .mixins.utils import type_checker
from ..utils.helpers import error_handler
class ClientsModel(ObjectDynamodb):
    '''
    Class used to handle clients.
    This class provides capability to store, retrieve, update and delete clients from AWS DynamoDB.
    '''
    def __init__(self, remote_table: str):
        super().__init__(remote_table)
        
    def get_clients(self):
        return self.get_items()

    @error_handler
    def get_client(self, client: dict):

        type_checker(client, [("connectionId", str)])

        return self.get_item(client)
    
    @error_handler
    def add_client(self, client: dict, query_params: dict):
        
        type_checker(client, [("connectionId", str)])
        type_checker(query_params, [("deviceType", str)])

        client["deviceType"] = query_params["deviceType"]

        return self.add_item(client)
    
    @error_handler
    def delete_client(self, client: dict):

        type_checker(client, [("connectionId", str)])

        return self.delete_item(client)
    
    @error_handler
    def set_device_type(self, client: dict, device_type: dict):

        type_checker(client, [("connectionId", str)])

        type_checker(device_type, [("deviceType", str)])

        return self.update_item(client, device_type)
    
    
    def filter_items(self, filters: dict = None):
        return self.scan_items(filters)