from .mixins.model_handler import ObjectDynamodb
from .mixins.validators import type_checker
from ..utils.helpers import error_handler, check_response

class DevicesModel(ObjectDynamodb):
    def __init__(self, devices_table: str):
        super().__init__(devices_table)

    def get_devices(self):
        '''
        Method that lists all registered devices.
        :returns : Response 200 containing devices in body or Response 500 error.
        '''
        return self.scan_items()
    
    def get_device(self, device: dict):

        return self.get_item(device)
    
    def get_connected_devices(self):
        response = self.scan_items()
        new_body = []
        for item in response["body"]:
            if item["connectionId"]:
                new_body.append(item)
        response["body"] = new_body
        return response
    
    def remove_connection(self, connection: dict):
        '''
        Method that searches for the device matching the connection and sets it to null if exists.
        :param dict `connection`: Dictionary containing key `connectionId` and value the connection_id.
        :returns : Response 200 or Error
        '''
        
        type_checker(connection, [("connectionId", str)])

        response_device = self.scan_items(connection)
        
        if check_response(response_device):
            device = response_device["body"][0]
            mac_address = {
                "macAddress": device["macAddress"]
            }

            response_device = self.update_item(mac_address, {"connectionId": None})
        
        return response_device

    @error_handler
    def set_device_name(self, mac_address: dict, device_name: dict):

        type_checker(mac_address, [("macAddress", str)])
        type_checker(device_name, [("deviceName", str)])

        return self.update_item(mac_address, device_name)

    @error_handler
    def get_connected_devices(self):

        response_devices = self.scan_items()

        if check_response(response_devices):
            new_list = []
            for device in response_devices["body"]:
                if device["connectionId"]:
                    new_list.append(device)
            response_devices["body"] = new_list
            
        return response_devices


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

        type_checker(connection, [("connectionId", str)])

        type_checker(query_params, [("deviceType", str)])
        
        if query_params["deviceType"] == "iot":
            type_checker(query_params, [("macAddress", str)])

            mac_address = {
                "macAddress": query_params["macAddress"]
                }
            #If the device is already registered then update its' connection id
            if check_response(self.get_item(mac_address)):
                response = self.update_item(mac_address, connection)
            else:
                response = self.add_item(item={
                    **mac_address,
                    **connection,
                    "deviceName": None,
                })
        return response
        