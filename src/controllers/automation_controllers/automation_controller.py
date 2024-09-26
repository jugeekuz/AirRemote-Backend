import json
import time
import boto3
from ...models import AutomationsModel
from ...utils.helpers import check_response
from .eventbridge_controller import create_eventbridge_schedule, delete_eventbridge_schedule, set_eventbridge_schedule_state


def create_automation(automations_model : AutomationsModel, lambda_arn: str, args: dict):
    
    scheduler = boto3.client('scheduler')

    attributes = ['automationName', 'buttonsList', 'cronExpression']
    
    if len(attributes)!=len(args) or not all(attr in args for attr in attributes):
        return {
            'statusCode': 400,
            'body': 'Received wrong arguments.'
        }

    automations_response = automations_model.add_automation({
                                "automationName": args["automationName"],
                                "buttonsList": args["buttonsList"]
                            })
    
    if not check_response(automations_response):
        return automations_response
    
    automation_id = automations_response['body']['automationId']

    _ = create_eventbridge_schedule(scheduler, automation_id, args['automationName'], lambda_arn, args['cronExpression'])

    return automations_response

    
def delete_automation(automations_model: AutomationsModel, args: dict):

    scheduler = boto3.client('scheduler')

    attributes = ['automationId']
    
    if len(attributes)!=len(args) or not all(attr in args for attr in attributes):
        return {
            'statusCode': 400,
            'body': 'Received wrong arguments.'
        }
    
    response = delete_eventbridge_schedule(scheduler, args["automationId"])

    if not check_response(response) :
        return response

    return automations_model.delete_automation({"automationId": args["automationId"]})


def set_automation_state(automations_model: AutomationsModel, args: dict, state: str):

    scheduler = boto3.client('scheduler')

    attributes = ['automationId']
    
    if len(attributes)!=len(args) or not all(attr in args for attr in attributes):
        return {
            'statusCode': 400,
            'body': 'Received wrong arguments.'
        }

    response = set_eventbridge_schedule_state(scheduler, args['automationId'], state)

    if not check_response(response):
        return response
    
    return automations_model.set_automation_state(args, state)

    

