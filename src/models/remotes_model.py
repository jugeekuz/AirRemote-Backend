from .mixins.model_handler import ObjectDynamodb
from .mixins.utils import type_checker
from ..utils.helpers import error_handler
class RemotesModel(ObjectDynamodb):
    '''
    Class used to handle remote control commands.
    This class provides capability to store, retrieve, update and delete remotes from AWS DynamoDB.
    '''
    def __init__(self, remote_table: str):
        super().__init__(remote_table)
        
    def get_remotes(self):
        '''
        Method used to list all saved remotes.
        :param bool `send`: Boolean signifying to send the response back to the connected device or not.
        :returns: Response 200 containing remotes in body or Response 500 error.
        '''
        
        return self.get_items()

    @error_handler
    def get_remote(self, remote: dict):
        '''
        Method used to get a remote by its' key.
        :param dict `remote`: Dictionary containing remote.
        :param bool `send`: Boolean signifying to send the response back to the connected device or not.
        :returns: Response 200 containing remotes in body or Response 500 error.
        '''

        type_checker(remote, [("remoteName", str)])        

        return self.get_item(remote)

    @error_handler
    def add_remote(self, remote: dict):

        keys = [("remoteName", str),
                ("macAddress", str), 
                ("commandSize", str),
                ("protocol", str),
                ("buttons", list)]
        
        type_checker(remote, keys)
        
        return self.add_item(remote)

    @error_handler
    def add_button(self, body: dict):
        keys = [("remoteName", str),
                ("buttonName", str),
                ("buttonCode", str)]
        
        type_checker(body, keys)
        
        remote = {"remoteName": body["remoteName"]}
        button = {"buttonName": body["buttonName"],
                  "buttonCode": body["buttonCode"]}

        return self.append_to_list(remote, "buttons", button)
    
    @error_handler
    def delete_remote(self, remote: dict):
        
        type_checker(remote, [("remoteName", str)])

        return self.delete_item(remote)
