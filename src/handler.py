import os
import json
import boto3
from .models.model_handler import ObjectDynamodb
from .websockets_handler.ws_module import WebSocket
from .controllers.remotes_controller import Remote

dynamo_db = boto3.client('dynamodb')
api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url=os.getenv("WSSAPIGATEWAYENDPOINT"))

def handle(event, context):
    try:
        connection_id = str(event["requestContext"]["connectionId"])
        routeKey = event["requestContext"]["routeKey"]
        
        #DynamoDB Models
        remote_model = ObjectDynamodb(dynamo_db, os.getenv("REMOTES_TABLE_NAME", ""))
        clients_model = ObjectDynamodb(dynamo_db, os.getenv("CLIENTS_TABLE_NAME", ""))
        iot_devices_model = ObjectDynamodb(dynamo_db, os.getenv("IOT_DEVICES_TABLE_NAME", ""))

        #WebSocket Gateway
        web_socket = WebSocket(api_gateway, clients_model)

        #Controllers
        remote_controller = Remote(remote_model, web_socket)

        if routeKey == "$connect":
            return web_socket.handle_connect(connection_id)
        elif routeKey == "$disconnect":
            return web_socket.handle_disconnect(connection_id)
        else:
            body = json.loads(event.get('body', ''))
            if body["type"] == "cmd":
                response = remote_controller.handle(body)
                web_socket.send_message(connection_id, response)

                return {"statusCode": 200,
                        "body": "OK"}
            
            elif body["type"] == "confirm":
    
            
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Bad Request"
        }

