import os
import json
from typing import Dict, Any
import boto3
from .wshandler.ws_module import WebSocket
from .remotehandler.remote_module import Remote

dynamo_db_client = boto3.client('dynamodb')
api_gateway_client = boto3.client('apigatewaymanagementapi', endpoint_url=os.getenv("WSSAPIGATEWAYENDPOINT"))

clients_table = os.getenv("CLIENTS_TABLE_NAME", "")
remotes_table = os.getenv("REMOTES_TABLE_NAME", "")

response_ok = {
    "statusCode": 200,
    "body": "Bad Request"
}


def handle(event, context):
    
    connection_id = str(event["requestContext"]["connectionId"])
    route_key = str(event["requestContext"]["routeKey"])
    body = event.get('body', '')
    if body:
        body = json.loads(body)

    web_socket = WebSocket(dynamo_db_client, api_gateway_client, clients_table)
    remote = Remote(dynamo_db_client, api_gateway_client, remotes_table)

    match (route_key):
        case "$connect":
            return web_socket.connect(connection_id)
        case "$disconnect":
            return web_socket.disconnect(connection_id)
        case _:
            match (body["type"]):
                case "info":
                    return response_ok
                case "error":
                    return response_ok
                case "cmd":
                    response = remote.handle_command(body)
                    web_socket.send_message_all("junk", response)
                    return response_ok

    #send error message
    return {
        "statusCode": 400,
        "body": "Bad Request"
    }

