from ..model_controllers.remotes_controller import RemoteController
class RemoteRouter:
    '''
    Class used to route incoming remote control commands.
    '''
    def __init__(self, remote: RemoteController):
        self.remote = remote
        

    def handle(self, body):
        match body['command']:
            case "getRemotes":
                return self.remote.get_remotes(send=True)
            
            case "getRemote":
                return self.remote.get_remote(body["remote"], send=True)
            
            case "addRemote":
                return self.remote.add_remote(body["remote"], send=True)
            
            case "addButton":
                return self.remote.add_button(body["remote"], body["button"], send=True)
            
            case "deleteRemote":
                return self.remote.delete_remote(body["remote"], send=True)
            
            case "sendCommandButton":
                return self.remote.send_command_button(body["macAddress"], body["remoteName"], body["buttonName"], send=True)

            case "requestButtonCode":
                return self.remote.request_button_code(body["macAddress"], body["remoteName"], body["buttonName"], send=True)
            
            case "registerButtonCode":
                return self.remote.register_button_code(body["macAddress"], body["buttonName"], body["buttonCode"], send=True)
 

            case _:
                return {
                    "statusCode": 400,
                    "body": "Bad Request"
                }

    