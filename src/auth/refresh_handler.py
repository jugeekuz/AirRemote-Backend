import json
import os
import boto3
from datetime import datetime, timedelta, time
from .utils import send_response
from http.cookies import SimpleCookie

cognito = boto3.client('cognito-idp')
CORS_ORIGIN = os.getenv('CORS_ORIGIN')

def handle(event, context):
    try:
        USER_POOL_ID = os.getenv('USER_POOL_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        cookies = event.get('headers', {}).get('cookie', '')
        if not cookies :
            cookies = event.get('headers', {}).get('Cookie', '')
        cors_headers = {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            "Access-Control-Allow-Credentials": True
        }
        if not cookies:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'message': 'Missing refresh token'})
            }
        refresh_token = extract_refresh_token(cookies)
        if not refresh_token:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'message': 'Missing refresh token'})
            }

        params = {
            'AuthFlow': 'REFRESH_TOKEN_AUTH',
            'UserPoolId': USER_POOL_ID,
            'ClientId': CLIENT_ID,
            'AuthParameters': {
                'REFRESH_TOKEN': refresh_token
            }
        }

        response = cognito.admin_initiate_auth(**params)
        new_access_token = response['AuthenticationResult']['AccessToken']
        new_id_token = response['AuthenticationResult'].get('IdToken')
        
        expires_in = response['AuthenticationResult']['ExpiresIn']
        expiration_time = datetime.utcnow() + timedelta(days=30)
        cookie = SimpleCookie()
        cookie['refreshToken'] = refresh_token
        cookie['refreshToken']['httponly'] = True
        cookie['refreshToken']['secure'] = True  
        cookie['refreshToken']['path'] = '/'
        cookie['refreshToken']['domain'] = '.air-remote.pro'
        cookie['refreshToken']['samesite'] = 'Strict'
        cookie['refreshToken']['expires'] = expiration_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                **cors_headers,
                "Set-Cookie": cookie.output(header='', sep='')
            },
            'body': json.dumps({
                'access_token': new_access_token,
                'id_token': new_id_token
            })
        }

    except cognito.exceptions.NotAuthorizedException:
        return send_response(401, {"message": "Invalid username or password"})

    except cognito.exceptions.UserNotFoundException:
        return send_response(404, {"message": "User not found"})

    except Exception as e:
        return send_response(500, {"message": "An error occurred", "error": str(e)})

def extract_refresh_token(cookies):
    """Extract the refresh token from cookies."""
    for cookie in cookies.split(';'):
        name, value = cookie.strip().split('=', 1)
        if name == 'refreshToken':
            return value
    return None