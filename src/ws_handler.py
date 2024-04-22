import os
import json
from .websockets.websockets_handler import WebSocket
from .models.clients_model import ClientsModel
from .models.devices_model import DevicesModel
from .models.remotes_model import RemotesModel
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

    clients_model = ClientsModel(CLIENTS_TABLE)
    devices_model = DevicesModel(DEVICES_TABLE)
    remotes_model = RemotesModel(REMOTES_TABLE)

    connection = {"connectionId": connection_id}

    match(route_key):
        case "$connect":
            response_devices = devices_model.set_device_status(connection, query_params)
            return clients_model.add_client(connection, query_params)
            
        case "$disconnect":
            response_devices = devices_model.remove_connection(connection)
            return clients_model.delete_client(connection)
        
        case "msg":
            return remotes_model.add_button(body)
            
        case _:
            return {
                "statusCode": 400,
                "body": f"Bad Request, route `{route_key}` does not exist."
            }

