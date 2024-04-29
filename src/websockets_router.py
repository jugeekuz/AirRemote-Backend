import os
import json
from .websockets.websockets_handler import WebSocket
from .model_controllers.clients_controller import ClientsModelController
from .model_controllers.devices_controller import DevicesModelController
from .model_controllers.remotes_controller import RemotesModelController
from .utils.helpers import error_handler

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE = os.getenv("REMOTES_TABLE_NAME", "")
CLIENTS_TABLE = os.getenv("CLIENTS_TABLE_NAME", "")
DEVICES_TABLE = os.getenv("IOT_DEVICES_TABLE_NAME", "")

@error_handler
def handle(event, context):
    connection_id = str(event["requestContext"]["connectionId"])
    route_key = str(event["requestContext"]["routeKey"])

    query_params = event.get('queryStringParameters', '')
    body = event.get('body', '')

    clients_controller = ClientsModelController(CLIENTS_TABLE)
    devices_controller = DevicesModelController(DEVICES_TABLE)
    remotes_controller = RemotesModelController(REMOTES_TABLE)

    connection = {"connectionId": connection_id}

    match(route_key):
        case "$connect":
            response_devices = devices_controller.set_device_status(connection, query_params)
            return clients_controller.add_client(connection, query_params)
            
        case "$disconnect":
            response_devices = devices_controller.remove_connection(connection)
            return clients_controller.delete_client(connection)
        
        case "msg":
            return remotes_controller.add_button(body)
            
        case _:
            return {
                "statusCode": 400,
                "body": f"Bad Request, route `{route_key}` does not exist."
            } 