import re
from .mixins.model_mixin import ObjectDynamodb
from .validators.remotes_validator import RemotesValidator
from ..utils.helpers import error_handler

class RemotesModelController(ObjectDynamodb):
    '''
    Class used to handle remote control commands.
    This class provides capability to store, retrieve, update and delete remotes from AWS DynamoDB.
    '''
    def __init__(self, remote_table: str):
        self.validator = RemotesValidator()
        super().__init__(remote_table)
        
 
    @error_handler
    def get_remotes(self, remote: dict = None):
        '''
        Method used to get a remote by its' key or all remotes if None.
        :param dict `remote`: Dictionary containing remote.
        :returns: Response 200 containing remotes in body or Response 500 error.
        '''
        if remote:
            
            self.validator.validate(remote, params=['remoteName'])

            return self.get_item(remote)
        else:

            return self.scan_items()

    @error_handler
    def add_remote(self, remote: dict):

        self.validator.validate(remote, params=['remoteName', 
                                                'macAddress', 
                                                'commandSize',
                                                'protocol',
                                                'buttons'])
        
        return self.add_item(remote)

    @error_handler
    def add_button(self, body: dict):
        
        remote = {"remoteName": body["remoteName"]}

        self.validator.validate(remote, params=['remoteName'])

        button = {"buttonName": body["buttonName"],
                  "buttonCode": body["buttonCode"]}
        
        self.validator.validate(button, params=['buttonName', 
                                                'buttonCode'])

        return self.append_to_list(remote, "buttons", button)
    
    @error_handler
    def delete_remote(self, remote: dict):
        
        self.validator.validate(remote, params=['remoteName'])

        return self.delete_item(remote)
