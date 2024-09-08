import re
from .mixins import ObjectDynamodb
from .validators import ClientsValidator
from ..utils.helpers import error_handler
            
class AutomationsModel(ObjectDynamodb):
    '''
    Class used to handle clients.
    This class provides capability to store, retrieve, update and delete clients from AWS DynamoDB.
    '''
    def __init__(self, clients_table: str):

        self.validator = ClientsValidator()

        super().__init__(clients_table)
        
    def get_automations(self):

        return self.scan_items()

    @error_handler
    def get_automation(self, automation: dict):

        self.validator.validate(client, params=['connectionId'])

        return self.get_item(automation)
    
    @error_handler
    def add_client(self, client: dict, query_params: dict):

        client["deviceType"] = query_params["deviceType"]

        self.validator.validate(client, params=['connectionId', 'deviceType'])

        return self.add_item(client)
    
    @error_handler
    def delete_client(self, client: dict):

        self.validator.validate(client, params=['connectionId'])

        return self.delete_item(client)
    
    @error_handler
    def set_device_type(self, client: dict, device_type: dict):

        self.validator.validate({**client, **device_type}, params=['connectionId', 'deviceType'])

        return self.update_item(client, device_type)
    
    
    def filter_items(self, filters: dict = None):

        if filters:
            self.validator.validate(filters)

        return self.scan_items(filters)