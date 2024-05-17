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
from ...utils.helpers import check_response
from ...utils.errors import InvalidRequestError
from .mixins.validator_mixin import BaseRequestValidator
class CMDValidator(BaseRequestValidator):
    def __init__(self):
        super().__init__()

    def check_button_read(self, request: dict, remote_response: dict, button_name: str):

        allowed_attributes = ["action", "cmd", "remoteName", "buttonName"]

        self.check_request(request, allowed_attributes)

        if remote_response['statusCode']==404 or remote_response['statusCode']==500:
            raise InvalidRequestError("Remote requested does not exist.")
        
        for btn in remote_response['body']['buttons']:
            if button_name == btn['buttonName']:
                raise InvalidRequestError('')

        
        
    def check_button_execute(self, request: dict):
        allowed_attributes = ["action", "cmd", "remoteName", "buttonName"]

        if not (all(isinstance(attr, str) for attr in request) \
                and all(attr in allowed_attributes for attr in request) \
                and (len(allowed_attributes) == len(request))):
            raise InvalidRequestError
        
    
    def validate(self, request: dict):

