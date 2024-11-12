from .mixins import ObjectDynamodb
from .validators import DevicesValidator
from ..utils.helpers import error_handler, check_response
from ..utils.errors import ResponseError
from ..controllers.security_controllers.utils import generate_salt, hash_token
class DevicesModel(ObjectDynamodb):
    def __init__(self, devices_table: str):

        self.validator = DevicesValidator()

        super().__init__(devices_table)

    def get_devices(self, device: dict = None):
        if device:
            self.validator.validate(device, params=['macAddress'])

            return self.get_item(device)  
        else:      
            return self.scan_items()

    @error_handler
    def add_unknown_device(self, item: dict):
        '''
        This method creates a temporary device whose MAC address is unknown yet.
        :param dict `item`: Dictionary containing key `deviceName` and `token`.
        :returns : Response 200 or Error
        '''

        device = {
            "macAddress": "FF:FF:FF:FF:FF:FF",
            "connectionId": None,
            "salt": generate_salt(),
            "deviceName": item["deviceName"]
        }

        device["hashToken"] = hash_token(item["token"], device["salt"])     
        
        response = self.get_devices()
        if response['statusCode'] != 200:
            return {
                'statusCode': 500,
                'body': 'Error while retrieving devices.'
            }
        
        new_order_index = str(len(response["body"]))

        for item in response["body"]:
            if item["macAddress"] == "FF:FF:FF:FF:FF:FF":
                new_order_index = str(len(response["body"])) - 1

        device['orderIndex'] = new_order_index

        self.validator.validate(device, params=['macAddress', 
                                                'connectionId',
                                                'salt',
                                                'hashToken',
                                                'orderIndex',
                                                'deviceName'])
        
        return self.add_item(device)

    @error_handler
    def add_device(self, item: dict):
        '''
        This method searches if a matching temporary MAC-less device entry exists and replaces it with the new MAC.
        :param dict `item`: Dictionary containing key `macAddress` and `token`.
        :returns : Response 200 or Error
        '''
        
        response = self.get_item({"macAddress": "FF:FF:FF:FF:FF:FF"})

        if not check_response(response):
            return {
                "statusCode": 400,
                "body": "Device doesn't exist."
            }
        
        saved_entry = response['body']

        hashed_token = hash_token(item["token"], saved_entry["salt"])

        if hashed_token != saved_entry["hashToken"]:
            return {
                "statusCode": 400,
                "body": "Token provided doesn't match configured one."
            }
        
        _ = self.delete_device({"macAddress": "FF:FF:FF:FF:FF:FF"})
        
        device = saved_entry
        device['macAddress'] = item['macAddress']
        
        self.validator.validate(device, params=['macAddress', 
                                                'connectionId',
                                                'salt',
                                                'orderIndex',
                                                'hashToken',
                                                'deviceName'])

        return self.add_item(device)

    @error_handler
    def delete_device(self, device: dict):
        
        self.validator.validate(device, params=['macAddress'])

        response = self.delete_item(device)
        
        if response['statusCode'] == 200:
            _ = self.clean_order_indexes('macAddress')

        return response

    @error_handler
    def get_connected_devices(self):
        '''
        Method that scans all devices and returns an array of devices that have connection id.
        '''
        response = self.scan_items()

        if not check_response(response):
            raise ResponseError(f"Unexpected response error when using `scan_items`, received status code {response['statusCode']} and body {response['body']}.")

        new_list = []
        for device in response["body"]:
            if device["connectionId"]:
                new_list.append(device)

        response["body"] = new_list
            
        return response

    @error_handler
    def remove_connection(self, connection: dict):
        '''
        Method that searches for the device matching the connection and sets it to null if exists.
        :param dict `connection`: Dictionary containing key `connectionId` and value the connection_id.
        :returns : Response 200 or Error
        '''
        response = self.scan_items(connection)
        
        if not check_response(response):
            raise ResponseError(f"Unexpected response error when using `scan_items`, received status code {response['statusCode']} and body {response['body']}.")
        
        device = response["body"][0]
        mac_address = {
            "macAddress": device["macAddress"]
        }

        self.validator.validate(mac_address, params=['macAddress'])

        return self.update_item(mac_address, {"connectionId": None})

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
        
        if query_params["deviceType"] == "iot":

            mac_address = {
                "macAddress": query_params["macAddress"]
                }
            
            self.validator.validate({**mac_address, **connection}, params=['macAddress','connectionId'])
            
            #If the device is already registered then update its' connection id
            if check_response(self.get_item(mac_address)):
                
                response = self.update_item(mac_address, connection)

            else:
                
                response = self.add_device({
                    "macAddress": query_params["macAddress"],
                    "token": query_params["token"]
                })

        return response
        