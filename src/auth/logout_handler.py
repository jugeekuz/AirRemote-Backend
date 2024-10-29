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
        cors_headers = {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            "Access-Control-Allow-Credentials": True
        }
        expiration_time = datetime.utcnow()
        cookie = SimpleCookie()
        cookie['refreshToken'] = ""
        cookie['refreshToken']['httponly'] = True
        cookie['refreshToken']['secure'] = True  
        cookie['refreshToken']['path'] = '/'
        cookie['refreshToken']['samesite'] = 'None'
        cookie['refreshToken']['expires'] = expiration_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                **cors_headers,
                "Set-Cookie": cookie.output(header='', sep='')
            },
            'body': json.dumps({
                'ok': 'true'
            })
        }

    except cognito.exceptions.NotAuthorizedException:
        return send_response(401, {"message": "Invalid username or password"})

    except cognito.exceptions.UserNotFoundException:
        return send_response(404, {"message": "User not found"})

    except Exception as e:
        return send_response(500, {"message": "An error occurred", "error": str(e)})
