import re
from .mixins.model_handler import ObjectDynamodb
from .validators.clients_validator import ClientsValidator
from ..utils.helpers import error_handler
            
class ClientsModel(ObjectDynamodb):
    '''
    Class used to handle clients.
    This class provides capability to store, retrieve, update and delete clients from AWS DynamoDB.
    '''
    def __init__(self, remote_table: str):
        self.validator = ClientsValidator()
        super().__init__(remote_table)
        
    def get_clients(self):
        return self.scan_items()

    @error_handler
    def get_client(self, client: dict):

        self.validator.validate(client)

        return self.get_item(client)
    
    @error_handler
    def add_client(self, client: dict, query_params: dict):

        client["deviceType"] = query_params["deviceType"]

        self.validator.validate(client)

        return self.add_item(client)
    
    @error_handler
    def delete_client(self, client: dict):

        self.validator.validate(client)

        return self.delete_item(client)
    
    @error_handler
    def set_device_type(self, client: dict, device_type: dict):

        self.validator.validate({**client, **device_type})

        return self.update_item(client, device_type)
    
    
    def filter_items(self, filters: dict = None):

        if filters:
            self.validator.validate(filters)

        return self.scan_items(filters)