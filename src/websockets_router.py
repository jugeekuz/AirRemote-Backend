import os
import json
from .models import RemotesModel, ClientsModel, DevicesModel, RequestPoolModel
from .websocket_controllers.cmd_controller import CMDController
from .websocket_controllers.ack_controller import ACKController
from .websocket_controllers.error_controller import ErrorController
from .utils.helpers import error_handler, check_response

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE, CLIENTS_TABLE, DEVICES_TABLE, REQUEST_POOL_TABLE = os.getenv("REMOTES_TABLE_NAME", ""), os.getenv("CLIENTS_TABLE_NAME", ""), os.getenv("IOT_DEVICES_TABLE_NAME", ""), os.getenv("REQUEST_POOL_TABLE_NAME", "")

remotes_model, clients_model, devices_model, requestpool_model = RemotesModel(REMOTES_TABLE), ClientsModel(CLIENTS_TABLE), DevicesModel(DEVICES_TABLE), RequestPoolModel(REQUEST_POOL_TABLE)

def connect(connection: dict, query_parameters: dict):
    '''
    Function handling new websocket connection by saving new clients and the device if it is a device
    '''

    if query_parameters['deviceType'] == 'iot':
        response_devices = devices_model.set_device_status(connection, query_parameters)
        if not check_response(response_devices):
            return response_devices
    
    return clients_model.add_client(connection, query_parameters)

def disconnect(connection: dict):
    '''
    Method handling websocket disconnects by deleting clients and setting device as disconnected (if it's a device).
    '''
    response_devices = devices_model.remove_connection(connection)
    
    return clients_model.delete_client(connection)


@error_handler
def handle(event, context):
    connection_id = str(event["requestContext"]["connectionId"])
    route_key = str(event["requestContext"]["routeKey"])
    query_params = event.get('queryStringParameters', '')
    print("here")
    body = event.get('body', '')
    body = json.loads(body) if body else ''
    print("here2")

    connection = {"connectionId": connection_id}

    cmd_controller = CMDController(WSSAPIGATEWAYENDPOINT, connection_id, requestpool_model, remotes_model, devices_model)
    print("1")
    ack_controller = ACKController(WSSAPIGATEWAYENDPOINT, connection_id, requestpool_model)
    print("2")
    error_controller = ErrorController(WSSAPIGATEWAYENDPOINT, connection_id, requestpool_model)

    print(route_key)

    websocket_router = {
        '$connect': lambda: connect(connection, query_params),
        '$disconnect': lambda: disconnect(connection),
        'cmd': lambda: cmd_controller.route(body),
        'ack': lambda: ack_controller.route(body),
        'error': lambda: error_controller.route(body)
    }

    return websocket_router[route_key]()


 