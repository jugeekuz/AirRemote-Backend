import json
import os
import boto3
from .utils import send_response, validate_input

cognito = boto3.client('cognito-idp')

def handle(event, context):
    try:
        is_valid = validate_input(event['body'])
        if not is_valid:
            return send_response(400, {'message': 'Invalid input'})

        body = json.loads(event['body'])
        email = body.get('email')
        nickname = body.get('nickname', "")  
        password = body.get('password')
        USER_POOL_ID = os.getenv('USER_POOL_ID')

        params = {
            'UserPoolId': USER_POOL_ID,
            'Username': email,
            'UserAttributes': [
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
                {
                    'Name': 'nickname',
                    'Value': nickname
                }
            ],
            'MessageAction': 'SUPPRESS'
        }

        response = cognito.admin_create_user(**params)
        
        if 'User' in response:
            params_for_set_pass = {
                'Password': password,
                'UserPoolId': USER_POOL_ID,
                'Username': email,
                'Permanent': True
            }
            cognito.admin_set_user_password(**params_for_set_pass)
        
        return send_response(200, {'message': 'User registration successful'})
    
    except Exception as error:
        message = str(error) if str(error) else 'Internal server error'
        return send_response(500, {'message': message})

