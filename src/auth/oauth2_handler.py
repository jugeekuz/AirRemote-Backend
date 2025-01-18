import json
import os
import urllib.error
import boto3
import sys
sys.path.insert(0, 'src/vendor')
import jwt
from datetime import datetime, timedelta
from .utils import send_response
from http.cookies import SimpleCookie
import urllib.parse
import urllib.request
from ..models import RegisteredUsersModel

cognito = boto3.client('cognito-idp')

def handle(event, context):
    try:
        COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')
        USER_POOL_ID = os.getenv('USER_POOL_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        CORS_ORIGIN = os.getenv('CORS_ORIGIN')
        USERS_MODEL = os.getenv('REGISTERED_USERS_TABLE_NAME')

        cors_headers = {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            "Access-Control-Allow-Credentials": True
        }
        
        body = event.get('body','')
        body = json.loads(body) if body else ''

        route_key = event["httpMethod"] + ' ' + event['resource']

        if route_key == "POST /auth/keep-alive":
            return send_response(200, {"message": "success"})

        body = json.loads(event.get('body', {}))
        code = body.get('code', {})
        state = body.get('state', {})

        if not code:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": 'Authorization code not found'}),
            }

        data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'code': code,
            'redirect_uri': f'{CORS_ORIGIN}/oauth2/callback'
        }
        encoded_data = urllib.parse.urlencode(data).encode("utf-8") 

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        request_url = f"{COGNITO_DOMAIN}/oauth2/token"
        request = urllib.request.Request(request_url, data=encoded_data, headers=headers, method='POST')
        try:

            with urllib.request.urlopen(request) as response:
                response_data = response.read().decode("utf-8")
                tokens = json.loads(response_data)

            if not isinstance(tokens, dict) or not ("refresh_token" in tokens):
                raise urllib.error.HTTPError
            
            # Check if user is registered by admin
            decoded_token = jwt.decode(tokens.get('id_token'), options={"verify_signature": False})

            # Extract the email from the decoded token
            email = decoded_token.get('email')

            users = RegisteredUsersModel(USERS_MODEL)
            user_response = users.get_user({"userEmail": email})
            if user_response['statusCode'] != 200:
                return send_response(403, {"message": "User hasn't been given access to the app"})
            
            expiration_time = datetime.utcnow() + timedelta(days=30)
            cookie = SimpleCookie()
            cookie['refreshToken'] = tokens.get("refresh_token")
            cookie['refreshToken']['httponly'] = True
            cookie['refreshToken']['secure'] = True  
            cookie['refreshToken']['path'] = '/'
            cookie['refreshToken']['domain'] = '.air-remote.pro'
            cookie['refreshToken']['samesite'] = 'Strict'
            cookie['refreshToken']['expires'] = expiration_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            
            return {
                "statusCode": 200,
                'headers': {
                    "Content-Type": "application/json",
                    **cors_headers,
                    "Set-Cookie": cookie.output(header='', sep='')
                },
                "body": json.dumps({
                    "access_token": tokens.get("access_token"),
                    "id_token": tokens.get("id_token")
                })
            }

        except urllib.error.HTTPError as e:
            error_message = e.read().decode("utf-8")
            return {
                "statusCode": e.code,
                **cors_headers,
                "body": json.dumps("Error exchanging authorization code for tokens")
            }

    except Exception as e:
        print(f"Exception: {e}")
        return {
            "statusCode": 500,
            **cors_headers,
            "body": json.dumps("Internal server error2")
        }
