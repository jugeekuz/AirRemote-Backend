import json
import os
import boto3
from .model_controllers.remotes_controller import RemotesModelController
from .model_controllers.devices_controller import DevicesModelController
# Initialize the Boto3 client for API Gateway
client = boto3.client('apigatewayv2')

REMOTES_TABLE = os.getenv("REMOTES_TABLE_NAME", "")
DEVICES_TABLE = os.getenv("IOT_DEVICES_TABLE_NAME", "")

remotes = RemotesModelController(REMOTES_TABLE)
devices = DevicesModelController(DEVICES_TABLE)


def handle(event, context):

    endpoint_router = {
        'GET /api/remotes': remotes.get_remotes,
        'GET /api/remotes/{remoteName}': lambda : remotes.get_remotes(event["pathParameters"]),
        
        'GET /api/devices': devices.get_devices,
        'GET /api/devices/{macAddress}': lambda : devices.get_devices(event["pathParameters"]),
        'GET /api/devices/connected': devices.get_connected_devices,
    }

    route_key = event["routeKey"]

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(endpoint_router[route_key](), indent=4)
    }