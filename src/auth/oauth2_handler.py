import json
import os
import urllib.error
import boto3
from datetime import datetime, timedelta
from .utils import send_response
from http.cookies import SimpleCookie
import urllib.parse
import urllib.request

cognito = boto3.client('cognito-idp')

def handle(event, context):
    try:
        COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')
        USER_POOL_ID = os.getenv('USER_POOL_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        CORS_ORIGIN = os.getenv('CORS_ORIGIN')

        cors_headers = {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            "Access-Control-Allow-Credentials": True
        }

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
        print(request)
        try:

            with urllib.request.urlopen(request) as response:
                response_data = response.read().decode("utf-8")
                print(response_data)
                tokens = json.loads(response_data)

            if not isinstance(tokens, dict) or not ("refresh_token" in tokens):
                raise urllib.error.HTTPError
            
            expiration_time = datetime.utcnow() + timedelta(days=30)
            cookie = SimpleCookie()
            cookie['refreshToken'] = tokens.get("refresh_token")
            cookie['refreshToken']['httponly'] = True
            cookie['refreshToken']['secure'] = True  
            cookie['refreshToken']['path'] = '/'
            cookie['refreshToken']['domain'] = '.air-remote.pro'
            cookie['refreshToken']['samesite'] = 'Strict'
            cookie['refreshToken']['expires'] = expiration_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            res = {
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
            print(res)
            return res
            # return {
            #     "statusCode": 200,
            #     'headers': {
            #         "Content-Type": "application/json",
            #         **cors_headers,
            #         "Set-Cookie": cookie.output(header='', sep='')
            #     },
            #     "body": json.dumps({
            #         "access_token": tokens.get("access_token"),
            #         "id_token": tokens.get("id_token")
            #     })
            # }

        except urllib.error.HTTPError as e:
            error_message = e.read().decode("utf-8")
            print(error_message)
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
