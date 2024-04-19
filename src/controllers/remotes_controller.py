from ..models.model_handler import ObjectDynamodb
from ..websockets.websockets_handler import WebSocket
class Remote:
    '''
    Class used to handle remote control commands.
    This class provides capability to store, retrieve, update and delete remotes from AWS DynamoDB.
    '''
    def __init__(self, remote_model: ObjectDynamodb,  websocket: WebSocket):
        self.remote_model = remote_model
        self.websocket = websocket
        

    def handle(self, body):
        match body['command']:
            case "getRemotes":
                return self.remote_model.get_items()
            
            case "getRemote":
                return self.remote_model.get_item(body["remote"])
            
            case "addRemote":
                return self.remote_model.add_item(body["remote"])
            
            case "addButton":
                return self.remote_model.append_to_list(body["remote"], "buttons", body["button"])
            
            case "deleteRemote":
                return self.remote_model.delete_item(body["remote"])
            
            case "sendCode":
                pass

            case "receiveCode":
                pass 

            case _:
                return {
                    "statusCode": 400,
                    "body": "Bad Request"
                }

    