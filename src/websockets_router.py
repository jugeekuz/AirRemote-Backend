import os
import json
from .models import RemotesModel, ClientsModel, DevicesModel, RequestPoolModel, AutomationsModel
from .controllers.websocket_controllers.cmd_controller import CMDController
from .controllers.websocket_controllers.ack_controller import ACKController
from .controllers.websocket_controllers.error_controller import ErrorController
from .utils.helpers import error_handler, check_response
from .controllers.security_controllers.utils import hash_token
from .controllers.security_controllers.token_controller import validate_websocket_jwt

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE, CLIENTS_TABLE, DEVICES_TABLE, REQUEST_POOL_TABLE, AUTOMATIONS_TABLE = os.getenv("REMOTES_TABLE_NAME", ""), os.getenv("CLIENTS_TABLE_NAME", ""), os.getenv("IOT_DEVICES_TABLE_NAME", ""), os.getenv("REQUEST_POOL_TABLE_NAME", ""), os.getenv("AUTOMATIONS_TABLE_NAME", "")

remotes_model, clients_model, devices_model, requestpool_model, automations_model = RemotesModel(REMOTES_TABLE), ClientsModel(CLIENTS_TABLE), DevicesModel(DEVICES_TABLE), RequestPoolModel(REQUEST_POOL_TABLE), AutomationsModel(AUTOMATIONS_TABLE)

def connect(connection: dict, query_parameters: dict):
    '''
    Function handling new websocket connection by saving new clients and the device if it is a device
    '''

    if query_parameters.get('deviceType') == 'iot':
        # Authorized through token
        # To be valid -> SHA-256(TOKEN+SALT)==Saved_Hashed_Token
        response_device = devices_model.get_devices({"macAddress": query_parameters["macAddress"]})
        if response_device["statusCode"] == 404:
            response = devices_model.add_device({"token": query_parameters["token"], "macAddress": query_parameters["macAddress"]})

            if not check_response(response):
                return response
        else : 

            device = response_device['body']
            hashed_token = hash_token(query_parameters['token'], device['salt'])
            if hashed_token != device['hashToken']:
                return {
                    'statusCode': 401,
                    'body': "Incorrect credentials."
                }
            
        
        response_devices = devices_model.set_device_status(connection, {"deviceType": query_parameters["deviceType"], "macAddress": query_parameters["macAddress"]})
        if not check_response(response_devices):
            return response_devices
        
    elif query_parameters.get('deviceType') == 'client':
        # Authorized through JWT
        jwt = query_parameters['jwt']
        res = validate_websocket_jwt(jwt)
        if not res['isAuthorized']:
            return {
                'statusCode': res['statusCode'],
                'body': res['body']
            }
        
    else :
        return {
            'statusCode': 400,
            'body': "Device Type not supported"
        }
    
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
    query_params = event.get('queryStringParameters', {})
    
    body = event.get('body', '')
    body = json.loads(body) if body else ''
    connection = {"connectionId": connection_id}

    cmd_controller = CMDController(WSSAPIGATEWAYENDPOINT, connection_id, requestpool_model, remotes_model, devices_model, automations_model)
    ack_controller = ACKController(WSSAPIGATEWAYENDPOINT, connection_id, requestpool_model, remotes_model, devices_model, automations_model)
    error_controller = ErrorController(WSSAPIGATEWAYENDPOINT, connection_id, requestpool_model, automations_model)
    print("hey")
    print(event)
    websocket_router = {
        '$connect': lambda: connect(connection, query_params),
        '$disconnect': lambda: disconnect(connection),
        'cmd': lambda: cmd_controller.route(body),
        'ack': lambda: ack_controller.route(body),
        'error': lambda: error_controller.route(body)
    }

    return websocket_router[route_key]()


 