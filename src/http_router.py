import json
import os
from .models import RemotesModel, ClientsModel, DevicesModel, RequestPoolModel, AutomationsModel, StatisticsModel
from .controllers.websocket_controllers.cmd_controller import CMDController
from .controllers.automation_controllers.automation_controller import create_automation
from .controllers.automation_controllers.automation_controller import create_automation, delete_automation, set_automation_state
from .controllers.cost_controllers.cost_controller import get_monthly_cost
from .auth.utils import send_response
from .controllers.security_controllers.token_controller import get_device_token, get_websocket_jwt
from urllib.parse import unquote

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE, CLIENTS_TABLE, DEVICES_TABLE, REQUEST_POOL_TABLE, AUTOMATIONS_TABLE, STATISTICS_TABLE = os.getenv("REMOTES_TABLE_NAME", ""), os.getenv("CLIENTS_TABLE_NAME", ""), os.getenv("IOT_DEVICES_TABLE_NAME", ""), os.getenv("REQUEST_POOL_TABLE_NAME", ""), os.getenv("AUTOMATIONS_TABLE_NAME", ""), os.getenv("STATISTICS_TABLE_NAME", "")
AUTOMATIONS_FUNCTION_ARN = os.environ.get('AUTOMATIONS_FUNCTION_ARN')
CORS_ORIGIN = os.getenv('CORS_ORIGIN')

remotes, clients, devices, requestpool, automations = RemotesModel(REMOTES_TABLE), ClientsModel(CLIENTS_TABLE), DevicesModel(DEVICES_TABLE), RequestPoolModel(REQUEST_POOL_TABLE), AutomationsModel(AUTOMATIONS_TABLE)

remotes = RemotesModel(REMOTES_TABLE)
devices = DevicesModel(DEVICES_TABLE)
automations = AutomationsModel(AUTOMATIONS_TABLE)
statistics = StatisticsModel(STATISTICS_TABLE)

def handle(event, context):
    body = event.get('body','')
    body = json.loads(body) if body else ''
    query_params = event.get('pathParameters','')

    route_key = event["httpMethod"] + ' ' + event['resource']

    if route_key == "POST /api/keep-alive":
        return send_response(200, {"message": "success"})
    
    cmd_controller = CMDController(WSSAPIGATEWAYENDPOINT, None, requestpool, remotes, devices, automations)

    endpoint_router = {
        #REMOTE ENDPOINTS
        'GET /api/remotes': lambda : remotes.get_remotes(),
        'POST /api/remotes': lambda: remotes.add_remote(body),
        'POST /api/remotes/sort': lambda: remotes.rearrange_items(body['newOrder'], 'remoteName'),
        'GET /api/remotes/{remoteName}': lambda : remotes.get_remotes({"remoteName" : unquote(query_params["remoteName"])}),
        'DELETE /api/remotes/{remoteName}': lambda : remotes.delete_remote({"remoteName" : unquote(query_params["remoteName"])}),
        'POST /api/remotes/{remoteName}/buttons': lambda: remotes.add_button({"remoteName" : unquote(query_params["remoteName"]),
                                                                              "buttonName" : body["buttonName"],
                                                                              "buttonCode" : body["buttonCode"]}),
        'POST /api/remotes/{remoteName}/buttons/sort': lambda: remotes.rearrange_list({"remoteName" : unquote(query_params["remoteName"])}, 'buttons', body['newOrder']),                                                 
        'DELETE /api/remotes/{remoteName}/buttons/{buttonName}': lambda : remotes.delete_button({"remoteName" : unquote(query_params["remoteName"]),
                                                                                                 "buttonName" : unquote(query_params["buttonName"])}),
        #DEVICE ENDPOINTS
        'GET /api/devices': lambda : devices.get_devices(),
        'POST /api/devices': lambda : devices.add_unknown_device(body),
        'POST /api/devices/sort': lambda : devices.rearrange_items(body['newOrder'], "macAddress"),
        'GET /api/devices/{macAddress}': lambda : devices.get_devices({"macAddress" : unquote(query_params["macAddress"])}),
        'PUT /api/devices/{macAddress}': lambda : devices.set_device_name({"macAddress" : unquote(query_params["macAddress"])},
                                                                          {"deviceName": body["deviceName"]}),
        'DELETE /api/devices/{macAddress}': lambda : devices.delete_device({"macAddress" : unquote(query_params["macAddress"])}),
        'GET /api/devices/connected': lambda : devices.get_connected_devices(),

        #AUTOMATION ENDPOINTS
        'GET /api/automations': lambda : automations.get_automations(),
        'GET /api/automations/{automationId}': lambda : automations.get_automation({"automationId": unquote(query_params["automationId"])}),
        'POST /api/automations': lambda : create_automation(automations, AUTOMATIONS_FUNCTION_ARN, body),
        'POST /api/automations/sort': lambda : automations.rearrange_items(body['newOrder'], 'automationId'),
        'DELETE /api/automations/{automationId}': lambda : delete_automation(automations, {"automationId": unquote(query_params["automationId"])}),
        'POST /api/automations/{automationId}/state': lambda : set_automation_state(automations, {"automationId": unquote(query_params["automationId"])}, body["state"]),
        'POST /api/automations/{automationId}/start': lambda : cmd_controller.automation_execute({"automationId": unquote(query_params["automationId"])}),
        'POST /api/automations/clean': lambda : automations.clean_expired_automations(),
        'GET /api/costs': lambda : statistics.get_statistics(),
        'GET /api/deviceToken': lambda : get_device_token(),

        'GET /api/websocketJwt': lambda : get_websocket_jwt(event['requestContext']['identity']['sourceIp']),
        'POST /api/devices/deleteme': lambda : devices.add_device(body),

    }

    cors_headers = {
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Origin': CORS_ORIGIN
    }

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps(endpoint_router[route_key](), indent=4)
    }