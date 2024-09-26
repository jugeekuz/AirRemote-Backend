import os
from .models import RemotesModel, ClientsModel, DevicesModel, RequestPoolModel, AutomationsModel
from .controllers.websocket_controllers.cmd_controller import CMDController

WSSAPIGATEWAYENDPOINT = os.getenv("WSSAPIGATEWAYENDPOINT")
REMOTES_TABLE, CLIENTS_TABLE, DEVICES_TABLE, REQUEST_POOL_TABLE, AUTOMATIONS_TABLE = os.getenv("REMOTES_TABLE_NAME", ""), os.getenv("CLIENTS_TABLE_NAME", ""), os.getenv("IOT_DEVICES_TABLE_NAME", ""), os.getenv("REQUEST_POOL_TABLE_NAME", ""), os.getenv("AUTOMATIONS_TABLE_NAME", "")


def handle(event, context):

    print(event)

    remotes, clients, devices, requestpool, automations = RemotesModel(REMOTES_TABLE), ClientsModel(CLIENTS_TABLE), DevicesModel(DEVICES_TABLE), RequestPoolModel(REQUEST_POOL_TABLE), AutomationsModel(AUTOMATIONS_TABLE)

    remotes = RemotesModel(REMOTES_TABLE)
    devices = DevicesModel(DEVICES_TABLE)
    automations = AutomationsModel(AUTOMATIONS_TABLE)

    cmd_controller = CMDController(WSSAPIGATEWAYENDPOINT, None, requestpool, remotes, devices, automations)

    if 'automationId' not in event:
        return {
            'statusCode': 400,
            'body': 'Bad request'
        }
    
    response = cmd_controller.automation_execute({"automationId": event['automationId']})

    return response