import boto3.dynamodb.conditions as conditions
from boto3.dynamodb.types import TypeDeserializer
from .mixins.mixin import ObjectDynamodb

class Remote(ObjectDynamodb):
    '''
    Class used to handle remote control commands.
    This class provides capability to store, retrieve, update and delete remotes from AWS DynamoDB.
    This class also can send and receive commands to/from remote IoT Device connected via WebSocket.
    '''
    def __init__(self, dynamo_db,  remotes_table):
        self.dynamo_db = dynamo_db
        self.remotes_table = remotes_table
        super().__init__(dynamo_db, remotes_table)

    
    def get_all_remotes(self):
        return self.get_items()

    def add_remote(self, remote: dict):
        return self.add_item(remote)

    def delete_remote(self, remote: dict):
        return self.delete_item(remote)

    def add_button(self, remote: dict, button: dict):
        return self.append_to_list(remote, "buttons", button)
     
    def get_remote(self, remote: dict):
        return self.get_item(remote)
        

    def handler(self, body):
        match body['command']:
            case "getRemotes":
                return self.get_all_remotes()
            
            case "getRemote":
                return self.get_remote(body["remote"])
            
            case "addRemote":
                return self.add_remote(body["remote"])
            
            case "addButton":
                return self.add_button(body["remote"], body["button"])
            
            case "deleteRemote":
                return self.delete_remote(body["remote"])
            
            case _:
                return {
                    "statusCode": 400,
                    "body": "Bad Request"
                }
                raise NotImplementedError

    