import json
import os
import boto3
from .models.remotes_model import RemotesModel
from .models.devices_model import DevicesModel

client = boto3.client('apigatewayv2')

REMOTES_TABLE = os.getenv("REMOTES_TABLE_NAME", "")
DEVICES_TABLE = os.getenv("IOT_DEVICES_TABLE_NAME", "")

remotes = RemotesModel(REMOTES_TABLE)
devices = DevicesModel(DEVICES_TABLE)


def handle(event, context):
    body = event.get('body','')
    body = json.loads(body) if body else ''
    query_params = event.get('pathParameters','')

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
    }

    route_key = event["routeKey"]

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(endpoint_router[route_key](), indent=4)
    }

