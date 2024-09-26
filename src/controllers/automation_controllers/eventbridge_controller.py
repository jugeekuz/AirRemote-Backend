import boto3
import json
import time
def create_eventbridge_role(lambda_arn: str):
    iam = boto3.client('iam')

    role_name = 'EventBridgeSchedulerRole'

    trust_relationship = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "scheduler.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship),
            Description="Role for EventBridge Scheduler to invoke Lambda for automation"
        )
        role_arn = response['Role']['Arn']

    except iam.exceptions.EntityAlreadyExistsException:        
        role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": lambda_arn
            }
        ]
    }

    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=f'EventBridgeSchedulerPolicy',
        PolicyDocument=json.dumps(policy_document)
    )

    time.sleep(1) # Let iam roles propagate slightly

    return role_arn


def create_eventbridge_schedule(scheduler, automation_id: str, automation_name: str, lambda_arn: str, schedule_expression: str):

    role_arn = create_eventbridge_role(lambda_arn)

    try:
        response = scheduler.create_schedule(
            Name=automation_id,
            Description=automation_name,
            ScheduleExpression=schedule_expression,
            FlexibleTimeWindow={
                'Mode': 'OFF'
            },
            Target={
                'Arn': lambda_arn,
                'RoleArn': role_arn,
                'Input': json.dumps({"automationId": automation_id}),
            }
        )
        return response
    except scheduler.exceptions.ValidationException as e:
        print(f"Validation error: {str(e)}")
        raise

def delete_eventbridge_schedule(scheduler, schedule_name: str):
    
    try:
        response = scheduler.delete_schedule(
            Name=schedule_name
        )
        return {
            'statusCode': 200,
            'body': "Schedule deleted successfully"
        }
    except scheduler.exceptions.ResourceNotFoundException:
        return {
            'statusCode': 404,
            'body': f"Schedule '{schedule_name}' not found."
        }
    except Exception as e:
        return {
            'statusCode': 404,
            'body': f"An error occurred while deleting schedule '{schedule_name}': {str(e)}"
        }
    
    
def set_eventbridge_schedule_state(scheduler, schedule_name: str, schedule_state: str):

    if schedule_state not in ['ENABLED', 'DISABLED']:
        return {
            'statusCode': 400,
            'body': f"State {schedule_state} not allowed"
        }

    try:
        current_schedule = scheduler.get_schedule(Name=schedule_name)

        response = scheduler.update_schedule(
            Name=schedule_name,
            State=schedule_state,
            ScheduleExpression=current_schedule.get('ScheduleExpression', ''),  
            FlexibleTimeWindow=current_schedule.get('FlexibleTimeWindow', {}),
            Target=current_schedule.get('Target', {}),  
            Description=current_schedule.get('Description', '') 
        )

        return {
            'statusCode': 200,
            'body': f"Schedule {schedule_state} successfully"
        }
    except scheduler.exceptions.ResourceNotFoundException:
        return {
            'statusCode': 404,
            'body': f"Schedule '{schedule_name}' not found."
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"An error occurred while setting schedule '{schedule_name}' state: {str(e)}"
        }