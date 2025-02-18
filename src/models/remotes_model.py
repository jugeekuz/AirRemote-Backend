import re
from .mixins import ObjectDynamodb
from .validators import RemotesValidator
from ..utils.helpers import error_handler, check_response
from ..utils.errors import ResponseError

class RemotesModel(ObjectDynamodb):
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

        response = self.get_remotes()
        if response['statusCode'] != 200:
            return {
                'statusCode': 500,
                'body': 'Error while retrieving remotes.'
            }
        
        new_order_index = str(len(response["body"]))

        button_clicks = {"buttonClicks": "0"}
        remote = {
            **remote, 
            **button_clicks,
            "orderIndex": new_order_index
            }

        self.validator.validate(remote, params=['remoteName', 
                                                'category',
                                                'macAddress', 
                                                'buttonClicks',
                                                'orderIndex',
                                                'buttons'])
        
        return self.add_item(remote)

    @error_handler
    def add_button(self, body: dict):
        '''
        Method used to add button to the list of buttons in a specific remote.
        This method also checks if given button matches the protocol's commandsize for given remote.
        :param dict `body`: Body passed as argument containing `remoteName`, `buttonName` and `buttonCode`.
        :returns: Response 200 or Response 500 error 
        '''
        remote = {"remoteName": body["remoteName"]}

        self.validator.validate(remote, params=['remoteName'])

        #Check what the protocol command size of this remote is to validate the buttonCode
        response = self.get_remotes(remote)
        
        if not check_response(response):
            raise ResponseError(f"Unexpected response error when using `get_remotes`, received status code {response['statusCode']} and body {response['body']}.")

        #Button code is temporarily a tuple of the code and command size for the validator to test if it matches
        button = {"buttonName": body["buttonName"].strip(),#AWS strips spaces from query param
                  "buttonCode": (body["buttonCode"], body["commandSize"]),
                  "commandSize": body["commandSize"],
                  "buttonState": body["buttonState"]}
        
        self.validator.validate(button, params=['buttonName', 
                                                'buttonCode',
                                                'commandSize',
                                                'buttonState'])
        
        #Button code is back to how it should be
        button['buttonCode'] = body["buttonCode"]

        return self.append_to_list(remote, "buttons", button)
    

    @error_handler
    def delete_button(self, body: dict):
        '''
        Method used to delete a button from the list of buttons in a specific remote.
        :param dict `body`: Body passed as argument containing `remoteName` and `buttonName` to delete from.
        :returns: Response 200 or Response 500 error 
        '''
        remote = {"remoteName": body["remoteName"]}

        self.validator.validate(remote, params=['remoteName'])

        response = self.get_remotes(remote)
        
        if not check_response(response):
            raise ResponseError(f"Unexpected response error when using `get_remotes`, received status code {response['statusCode']} and body {response['body']}.")
        
        button = {'buttonName' : body['buttonName']}

        self.validator.validate(button, ['buttonName'])
        
        return self.delete_from_list(remote, 'buttons', button) 
        

    @error_handler
    def delete_remote(self, remote: dict):
        
        self.validator.validate(remote, params=['remoteName'])

        response = self.delete_item(remote)

        if response['statusCode'] == 200:
            res = self.clean_order_indexes('remoteName')

        return response

    @error_handler
    def get_button(self, remote: dict, button: dict):

        self.validator.validate(button, params=['buttonName'])

        for btn in remote['buttons']:
            if btn['buttonName'] == button['buttonName']:

                return {"statusCode": 200,
                        "body": btn}
            
        return {"statusCode": 404,
                "body": "Button does not exist."}
    
    @error_handler
    def increment_counter(self, remote: dict):

        self.validator.validate(remote, params=['remoteName'])

        remote_response = self.get_remotes(remote)

        if not check_response(remote_response):
            return remote_response
        
        counter = int(remote_response['body']['buttonClicks']) + 1

        return self.update_item(remote, {'buttonClicks': str(counter)})
