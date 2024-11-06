import json
import os
import boto3
from datetime import datetime, timedelta, time
from .utils import send_response, validate_input
from http.cookies import SimpleCookie

cognito = boto3.client('cognito-idp')
CORS_ORIGIN = os.getenv('CORS_ORIGIN')

def handle(event, context):
    try:
        cors_headers = {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            "Access-Control-Allow-Credentials": 'true'
        }
        is_valid = validate_input(event['body'])
        if not is_valid:
            return send_response(400, {'message': 'Invalid input'})

        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')
        USER_POOL_ID = os.getenv('USER_POOL_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')

        params = {
            'AuthFlow': 'ADMIN_NO_SRP_AUTH',
            'UserPoolId': USER_POOL_ID,
            'ClientId': CLIENT_ID,
            'AuthParameters': {
                'USERNAME': email,
                'PASSWORD': password
            }
        }

        response = cognito.admin_initiate_auth(**params)

        access_token = response['AuthenticationResult']['AccessToken']
        id_token = response['AuthenticationResult']['IdToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        expires_in = response['AuthenticationResult']['ExpiresIn']
        expiration_time = datetime.utcnow() + timedelta(days=30)

        cookie = SimpleCookie()
        cookie['refreshToken'] = refresh_token
        cookie['refreshToken']['httponly'] = True
        cookie['refreshToken']['secure'] = True  
        cookie['refreshToken']['path'] = '/'
        cookie['refreshToken']['samesite'] = 'None'
        cookie['refreshToken']['expires'] = expiration_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT") 
        response_data = {
            "message": "Login successful",
            "access_token": access_token,
            "id_token": id_token
        }

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                **cors_headers,
                "Set-Cookie": cookie.output(header='', sep='')
            },
            "body": json.dumps(response_data)
        }

        return response

    except cognito.exceptions.NotAuthorizedException:
        return send_response(401, {"message": "Invalid username or password"})

    except cognito.exceptions.UserNotFoundException:
        return send_response(404, {"message": "User not found"})

    except Exception as e:
        return send_response(500, {"message": "An error occurred", "error": str(e)})
