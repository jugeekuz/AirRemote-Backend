import json
import os
import boto3
from .models import RemotesModel, ClientsModel, DevicesModel, RequestPoolModel, AutomationsModel
from .controllers.websocket_controllers.cmd_controller import CMDController

client = boto3.client('apigatewayv2')

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE, CLIENTS_TABLE, DEVICES_TABLE, REQUEST_POOL_TABLE, AUTOMATIONS_TABLE = os.getenv("REMOTES_TABLE_NAME", ""), os.getenv("CLIENTS_TABLE_NAME", ""), os.getenv("IOT_DEVICES_TABLE_NAME", ""), os.getenv("REQUEST_POOL_TABLE_NAME", ""), os.getenv("AUTOMATIONS_TABLE_NAME", "")

remotes, clients, devices, requestpool, automations = RemotesModel(REMOTES_TABLE), ClientsModel(CLIENTS_TABLE), DevicesModel(DEVICES_TABLE), RequestPoolModel(REQUEST_POOL_TABLE), AutomationsModel(AUTOMATIONS_TABLE)

remotes = RemotesModel(REMOTES_TABLE)
devices = DevicesModel(DEVICES_TABLE)
automations = AutomationsModel(AUTOMATIONS_TABLE)

def handle(event, context):
    body = event.get('body','')
    body = json.loads(body) if body else ''
    query_params = event.get('pathParameters','')
    
    cmd_controller = CMDController(WSSAPIGATEWAYENDPOINT, None, requestpool, remotes, devices, automations)

    endpoint_router = {
        #REMOTE ENDPOINTS
        'GET /api/remotes': lambda : remotes.get_remotes(),
        'POST /api/remotes': lambda: remotes.add_remote(body),
        'GET /api/remotes/{remoteName}': lambda : remotes.get_remotes({"remoteName" : query_params["remoteName"]}),
        'DELETE /api/remotes/{remoteName}': lambda : remotes.delete_remote({"remoteName" : query_params["remoteName"]}),
        'POST /api/remotes/{remoteName}/buttons': lambda: remotes.add_button({"remoteName" : query_params["remoteName"],
                                                                              "buttonName" : body["buttonName"],
                                                                              "buttonCode" : body["buttonCode"]}),                                                                        
        'DELETE /api/remotes/{remoteName}/buttons/{buttonName}': lambda : remotes.delete_button({"remoteName" : query_params["remoteName"],
                                                                                                 "buttonName" : query_params["buttonName"]}),
        #DEVICE ENDPOINTS
        'GET /api/devices': lambda : devices.get_devices(),
        'POST /api/devices': lambda : devices.add_device(body),
        'GET /api/devices/{macAddress}': lambda : devices.get_devices({"macAddress" : query_params["macAddress"]}),
        'PUT /api/devices/{macAddress}': lambda : devices.set_device_name({"macAddress" : query_params["macAddress"]},
                                                                          {"deviceName": body["deviceName"]}),
        'DELETE /api/devices/{macAddress}': lambda : devices.delete_device({"macAddress" : query_params["macAddress"]}),
        'GET /api/devices/connected': lambda : devices.get_connected_devices(),

        'GET /api/automations': lambda : automations.get_automations(),
        'GET /api/automations/{automationId}': lambda : automations.get_automation({"automationId": query_params["automationId"]}),
        'POST /api/automations': lambda : automations.add_automation(body),
        'DELETE /api/automations/{automationId}': lambda : automations.delete_automation({"automationId": query_params["automationId"]}),
        'PUT /api/automations/{automationId}/increment': lambda : automations.increment_counter({"automationId": query_params["automationId"]}),
        'PUT /api/automations/clean': lambda : automations.clean_expired_automations(),

        'POST /api/automations/{automationId}/start': lambda : cmd_controller.automation_execute({"automationId": query_params["automationId"]}),
    }

    route_key = event["routeKey"]
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(endpoint_router[route_key](), indent=4)
    }

