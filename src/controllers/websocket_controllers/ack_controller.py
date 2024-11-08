import json
from .mixins.websocket_mixins import WebSocketMixin
from ...models import RequestPoolModel, RemotesModel, AutomationsModel, DevicesModel
from .validators.ack_validator import ACKValidator
from .cmd_controller import CMDController
from ...utils.helpers import error_handler, check_response

class ACKController(WebSocketMixin):
    def __init__(self, 
                 endpoint_url: str, 
                 connection_id: str,
                 requestpool_model: RequestPoolModel,
                 remotes_model: RemotesModel,
                 devices_model: DevicesModel,
                 automations_model: AutomationsModel):
        
        self.endpoint_url = endpoint_url
        self.requestpool_model = requestpool_model
        self.remotes_model = remotes_model
        self.automations_model = automations_model
        self.devices_model = devices_model

        self.validator = ACKValidator(requestpool_model, remotes_model)

        super().__init__(endpoint_url, connection_id)


    @WebSocketMixin.notify_if_error
    def handle_ack_read(self, message: dict):    
        '''
        Method that receives an acknowledgment message that request with `request_id` was carried out successfully and forwards the message to the client who requested it originally.
        :param dict `message`: Acknowledgement message that must contain `request_id`.
        :return : Response of the attempt to send the message to the websocket connection.
        '''
        self.validator.validate_ack_read(message)

        requestpool_response = self.requestpool_model.get_requests({'requestId': message['requestId']})

        requestpool_entry = requestpool_response['body']

        requestpool_response = self.requestpool_model.delete_request({'requestId': requestpool_entry['requestId']})

        original_request = json.loads(requestpool_entry['requestBody'])
    
        button = {
            "remoteName": original_request['remoteName'],
            "buttonName": original_request['buttonName'],
            "commandSize": message['commandSize'],
            "buttonCode": message['buttonCode'],
            "buttonState": original_request['buttonState']
        }

        button_response = self.remotes_model.add_button(button)
        
        ack_message = {
            'action': 'ack',
            'requestId': requestpool_entry['requestId'],
            'body': 'success'
        }

        return self.send_message(ack_message, requestpool_entry['connectionId'])
    
    @WebSocketMixin.notify_if_error
    def handle_ack_execute(self, message: dict):    
        '''
        Method that receives an acknowledgment message that request with `request_id` was carried out successfully and forwards the message to the client who requested it originally.
        :param dict `message`: Acknowledgement message that must contain `request_id`.
        :return : Response of the attempt to send the message to the websocket connection.
        '''
        self.validator.validate_ack_execute(message)

        requestpool_response = self.requestpool_model.get_requests({'requestId': message['requestId']})
        requestpool_entry = requestpool_response['body']
        requestpool_response = self.requestpool_model.delete_request({'requestId': requestpool_entry['requestId']})

        original_request = json.loads(requestpool_entry['requestBody'])

        ack_message = {
            'action': 'ack',
            'requestId': requestpool_entry['requestId'],
            'body': 'success'
        }

        return self.send_message(ack_message, requestpool_entry['connectionId'])    
    
    
    def handle_ack_automate(self, message: dict):
        
        automations_response = self.automations_model.increment_counter({"automationId": message["automationId"]})
        
        if automations_response["body"] == "Automation Finished":
            return automations_response     
           
        cmd_controller = CMDController(self.endpoint_url, None, self.requestpool_model, self.remotes_model, self.devices_model, self.automations_model)

        return cmd_controller.automation_execute({"automationId": message["automationId"]})


    @WebSocketMixin.notify_if_error
    def route(self, request: dict):
        if 'buttonCode' in request:
            return self.handle_ack_read(request)
        elif 'automationId' in request:
            return self.handle_ack_automate(request)
        else:
            return self.handle_ack_execute(request)