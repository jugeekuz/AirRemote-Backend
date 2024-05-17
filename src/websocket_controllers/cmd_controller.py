from .mixins.websocket_mixins import WebSocketMixinV2
from ..models import RequestPoolModel, RemotesModel, DevicesModel
from ..utils.helpers import error_handler, check_response
class CMDController(WebSocketMixinV2):
    def __init__(self, 
                 endpoint_url: str, 
                 connection_id: str,
                 request_pool_model: RequestPoolModel,
                 remotes_model: RemotesModel,
                 devices_model: DevicesModel):
        
        self.request_pool_model = request_pool_model
        self.remotes_model = remotes_model
        self.devices_model = devices_model

        super().__init__(endpoint_url, connection_id, devices_model)   

        
    @error_handler
    def button_read(self, request: dict):
        '''
        Method that receives request to read a button, saves that request to RequestPoolModel and forwards that request to a given device.
        :param dict request: Message containing the request sent from the frontend
        :return : Response of the attempt to send the message to the websocket connection. 
        '''
        remote_res = self.remotes_model.get_remotes({'remoteName': request['remoteName']})

        self.request_pool_model.clean_expired_requests()
        requestpool_res = self.request_pool_model.add_request(self.websocket.connection_id, request)

        iot_command = {
            'action': 'cmd',
            'cmd': 'read',
            'protocol': remote_res['body']['protocol'],
            'commandSize': remote_res['body']['commandSize'],
            'requestId': requestpool_res['body']['requestId']
        }

        return self._send_message_device({'macAddress': remote_res['body']['macAddress']}, iot_command)
        

    @error_handler
    def button_execute(self, request: dict):
        '''
        Method that receives request to execute a button, finds and saves that request to RequestPoolModel and forwards that request to a given device.
        :param dict `request`: Message containing the request sent from the frontend
        :return : Response of the attempt to send the message to the websocket connection. 
        '''
        remote_res = self.remotes_model.get_remotes({'remoteName': request['remoteName']})
        button_res = self.remotes_model.get_button(remote_res['body'],
                                                   {'buttonName': request['buttonName']},
                                                   from_remote=True)
        
        self.request_pool_model.clean_expired_requests()
        requestpool_res = self.request_pool_model.add_request(self.websocket.connection_id, request)

        iot_command = {
            'action': 'cmd',
            'cmd': 'execute',
            'protocol': remote_res['body']['protocol'],
            'commandSize': remote_res['body']['commandSize'],
            'buttonCode' : button_res['body']['buttonCode'],
            'requestId': requestpool_res['body']['requestId']
        }

        return self._send_message_device({'macAddress': remote_res['body']['macAddress']}, iot_command)
    
    @error_handler
    def route(self, request: dict):
        if request['cmd'] == 'read':
            return self.button_read(request)
        else:
            return self.button_execute(request)