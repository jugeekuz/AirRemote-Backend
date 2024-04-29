from .mixins.model_mixin import ObjectDynamodb
from .validators.devices_validator import DevicesValidator
from ..utils.helpers import error_handler, check_response

class DevicesModelController(ObjectDynamodb):
    def __init__(self, devices_table: str):
        self.validator = DevicesValidator()
        super().__init__(devices_table)

    def get_devices(self, device: dict = None):
        '''
        Method that lists all registered devices.
        :param dict `device`: Device to search for or None to search all
        :returns : Response 200 containing devices in body or Response 500 error.
        '''
        if device:
            self.validator.validate(device, params=['macAddress'])

            return self.get_item(device)  
        else:      
            return self.scan_items()

    
    @error_handler
    def get_connected_devices(self):
        '''
        Method that scans all devices and returns an array of devices that have connection id.
        '''
        response = self.scan_items()
        if check_response(response):
            new_list = []
            for device in response["body"]:
                if device["connectionId"]:
                    new_list.append(device)

            response["body"] = new_list
            
        return response

    
    def remove_connection(self, connection: dict):
        '''
        Method that searches for the device matching the connection and sets it to null if exists.
        :param dict `connection`: Dictionary containing key `connectionId` and value the connection_id.
        :returns : Response 200 or Error
        '''
        response_device = self.scan_items(connection)
        
        if check_response(response_device):
            device = response_device["body"][0]
            mac_address = {
                "macAddress": device["macAddress"]
            }

            self.validator.validate(mac_address, params=['macAddress'])

            response_device = self.update_item(mac_address, {"connectionId": None})
        
        return response_device

    @error_handler
    def set_device_name(self, mac_address: dict, device_name: dict):
        '''
        Method that sets device name
        :param dict `mac_address`: Dictionary containing key `macAddress` and valid mac address as value
        :param dict `device_name`: Dictionary containing key `deviceName` and valid device name as value
        :returns : Response 200 or Error
        '''

        self.validator.validate({**mac_address, **device_name}, params=['macAddress, deviceName'])

        return self.update_item(mac_address, device_name)

    


    @error_handler
    def set_device_status(self, connection: dict, query_params: dict):
        '''
        Method used to handle messages from devices declaring their device type and their MAC address potentially.

        The dict `query_params` should contain key-value pairs in one of two formats:
        {
            "deviceType": "iot",
            "macAddress": "00:B0:D0:63:C2:26"
        }
        - OR -
        {
            "deviceType": "someOtherType"
        }

        :param str `connection_id`: The connection ID of the connection we received message from.
        :param dict `query_params`: The query_params of the request sent to API Gateway
        :return : Response 201 or Response 500
        '''
        
        if query_params["deviceType"] == "iot":

            mac_address = {
                "macAddress": query_params["macAddress"]
                }
            #If the device is already registered then update its' connection id
            if check_response(self.get_item(mac_address)):

                self.validator.validate({**mac_address, **connection}, params=['macAddress','connectionId'])

                response = self.update_item(mac_address, connection)

            else:

                response = self.add_item(item={
                    **mac_address,
                    **connection,
                    "deviceName": None,
                })

        return response
        