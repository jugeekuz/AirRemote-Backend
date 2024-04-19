from ..model_controllers.devices_controller import DeviceController
class DeviceRouter:
    '''
    Class used to route incoming remote control commands.
    '''
    def __init__(self, device: DeviceController):
        self.device = device

        

    def handle(self, body, **kwargs):
        match body['command']:
            case "setStatus":
                if "connectionId" in kwargs:
                    return self.device.set_device_status(kwargs["connectionId"], body)

            case _:
                return {
                    "statusCode": 400,
                    "body": "Bad Request"
                }

    