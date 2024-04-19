import os
import json
from .websockets.websockets_handler import WebSocket
from .model_controllers.remotes_controller import RemoteController
from .model_controllers.clients_controller import ClientsController
from .model_controllers.devices_controller import DeviceController
from .routes.remotes_routes import RemoteRouter
from .routes.devices_routes import DeviceRouter
from .utils.helpers import check_response, error_handler

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE = os.getenv("REMOTES_TABLE_NAME", "")
CLIENTS_TABLE = os.getenv("CLIENTS_TABLE_NAME", "")
DEVICES_TABLE = os.getenv("IOT_DEVICES_TABLE_NAME", "")

@error_handler
def handle(event, context):
    connection_id = str(event["requestContext"]["connectionId"])
    route_key = str(event["requestContext"]["routeKey"])
    
    #WebSocket Gateway
    web_socket = WebSocket(WSSAPIGATEWAYENDPOINT, CLIENTS_TABLE, REMOTES_TABLE)

    #Controllers
    remote_controller = RemoteController(REMOTES_TABLE, web_socket)
    clients_controller = ClientsController(CLIENTS_TABLE, web_socket)
    device_controller = DeviceController(DEVICES_TABLE, web_socket)

    #Routers
    remote_router = RemoteRouter(remote_controller)
    device_router = DeviceRouter(device_controller)
    match(route_key):
        case "$connect":
        
            response = clients_controller.add_client({
                "connectionId": connection_id,
                "deviceType": None
            })

            return response
        
        case "$disconnect":

            connection = {"connectionId": connection_id}

            response_device = device_controller.remove_connection(connection)

            return clients_controller.delete_client(connection)
        
        case "cmd":
            body = json.loads(event.get('body', ''))

            if body["type"] == "remote":
                return remote_router.handle(body)
            elif body["type"] == "device":
                return device_router.handle(body)
            else:
                raise NotImplementedError
            
        case _:
            return {
                "statusCode": 400,
                "body": f"Bad Request, route `{route_key}` does not exist."
            }

