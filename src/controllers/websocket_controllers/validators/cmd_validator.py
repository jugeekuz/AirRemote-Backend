'''
Allowed Websocket Requests:

*** READ A BUTTON
- 1:
    -- INCOMING REQUEST
        **Request to read a button (Frontend -> Lambda Function)**
            * Source: Frontend
            * Destination: Lambda Function
            * Description: Request coming from the frontend to read a button and add it to a given remote with a given name.
            * Example Format: 
                ```json
                {
                    "action": "cmd",
                    "cmd": "read",
                    "remoteName": "SharpTV",
                    "buttonName": "Power"
                }
                ```
    -- OUTGOING REQUEST
        **Request to read a button (Lambda Function -> IoT Device)**
            * Source: Lambda Function
            * Destination: IoT Device
            * Description: Request forwarded from the Lambda Function instructing the IoT device to read a button with given protocol.
            * Example Format: 
                ```json
                {
                    "action": "cmd",
                    "cmd": "read",
                    "protocol": "NAC",
                    "commandSize": "32",
                    "requestId": "1sP_1715872238.16489"
                }
                ```
- 2:
    -- INCOMING REQUEST
        **Reply from IoT Device that a button was read (IoT Device -> Lambda Function)**
            * Source: IoT Device
            * Destination: Lambda Function
            * Description: Reply sent from the IoT device, along with the button code it read, instructing Lambda to forward the success message to the original requester.
            * Example Format: 
                ```json
                {
                    "action": "ack",
                    "buttonCode": "0xDEADBEEF21",
                    "requestId": "1sP_1715872238.16489"
                }
                ```
    -- OUTGOING REQUEST
        **Informing of frontend that button was read successfully (Lambda Function -> Frontend)**
            * Source: Lambda Function
            * Destination: Frontend
            * Description: Reply from Lambda Function acknowledging that the front end's request was executed.
            * Example Format: 
                ```json
                {
                    "action": "ack",
                    "requestId": "1sP_1715872238.16489"
                }
                ```

*** EXECUTE A BUTTON
- 1:
    -- INCOMING REQUEST
        **Request to execute a button (Frontend -> Lambda Function)**
            * Source: Frontend
            * Destination: Lambda Function
            * Description: Request coming from the frontend to execute a button of a given remote.
            * Example Format: 
                ```json
                {
                    "action": "cmd",
                    "cmd": "execute",
                    "remoteName": "SharpTV",
                    "buttonName": "Power"
                }
                ```
    -- OUTGOING REQUEST
        **Request to read a button (Lambda Function -> IoT Device)**
            * Source: Lambda Function
            * Destination: IoT Device
            * Description: Request forwarded from the Lambda Function instructing the IoT device to read a button with given protocol.
            * Example Format: 
                ```json
                {
                    "action": "cmd",
                    "cmd": "execute",
                    "protocol": "NAC",
                    "commandSize": "32",
                    "buttonCode": "0xDEADBEEF21",
                    "requestId": "1sP_1715872238.16489"
                }
                ```
- 2:
    -- INCOMING REQUEST
        **Reply from IoT Device that a button was executed (IoT Device -> Lambda Function)**
            * Source: IoT Device
            * Destination: Lambda Function
            * Description: Reply sent from the IoT device instructing Lambda to forward the success message to the original requester.
            * Example Format: 
                ```json
                {
                    "action": "ack",
                    "requestId": "1sP_1715872238.16489"
                }
                ```
    -- OUTGOING REQUEST
        **Informing of frontend that button was executed successfully (Lambda Function -> Frontend)**
            * Source: Lambda Function
            * Destination: Frontend
            * Description: Reply from Lambda Function acknowledging that the front end's request was executed.
            * Example Format: 
                ```json
                {
                    "action": "ack",
                    "requestId": "1sP_1715872238.16489"
                }
                ```


'''
import re
from ....models import DevicesModel, RemotesModel
from ....utils.errors import InvalidRequestError
from .mixins.validator_mixin import BaseRequestValidator
class CMDValidator(BaseRequestValidator):
    def __init__(self, remotes_model: RemotesModel, devices_model: DevicesModel):
        self.remotes_model = remotes_model
        self.devices_model = devices_model
        super().__init__()

    def validate_button_read(self, request: dict):

        allowed_attributes = ["action", "cmd", "remoteName", "buttonName"]

        self.check_request(request, allowed_attributes)

        pattern = '^[a-zA-Z0-9- ]+$'

        if not re.match(pattern, request['buttonName']):
            raise InvalidRequestError('Button Name is invalid.')

        remote_response = self.remotes_model.get_remotes({"remoteName": request["remoteName"]})

        if remote_response['statusCode']==404 or remote_response['statusCode']==500:
            raise InvalidRequestError('Remote requested does not exist.')
        
        for btn in remote_response['body']['buttons']:
            if request['buttonName'] == btn['buttonName']:
                raise InvalidRequestError('Button with that name already exists.')

        devices_response = self.devices_model.get_devices({"macAddress": remote_response['body']['macAddress']})

        if devices_response["statusCode"] == 404 or devices_response["statusCode"] == 500:
            raise InvalidRequestError('Device does not exist.')
        
        if devices_response["statusCode"] == 200 and devices_response["body"]["connectionId"] is None:
            raise InvalidRequestError('Device is not connected.')
        
        
    def validate_button_execute(self, request: dict):

        allowed_attributes = ["action", "cmd", "remoteName", "buttonName"]

        self.check_request(request, allowed_attributes)

        remote_response = self.remotes_model.get_remotes({"remoteName": request["remoteName"]})

        if remote_response['statusCode']==404 or remote_response['statusCode']==500:
            raise InvalidRequestError('Remote requested does not exist.')
        
        button_exists = False
        for btn in remote_response['body']['buttons']:
            if request['buttonName'] == btn['buttonName']:
                button_exists = True

        if not button_exists:
            raise InvalidRequestError('Button requested does not exist.')

        devices_response = self.devices_model.get_devices({"macAddress": remote_response['body']['macAddress']})
        if devices_response["statusCode"] == 404 or devices_response["statusCode"] == 500:
            raise InvalidRequestError('Device does not exist.')
        
        if devices_response["statusCode"] == 200 and devices_response["body"]["connectionId"] is None:
            raise InvalidRequestError('Device is not connected.')
    
