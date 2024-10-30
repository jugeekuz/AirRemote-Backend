import json
import sys
import os
from dotenv import load_dotenv 
sys.path.insert(0, 'src/vendor')
from jwt import ExpiredSignatureError, InvalidTokenError
from .utils import generate_token, generate_salt, hash_token, generate_jwt, validate_jwt
load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')

def get_device_token():
    return {
        'statusCode': 200,
        'body': {
            'deviceToken': generate_token()
        }
    }

def get_websocket_jwt(userArn):
    try:
        token = generate_jwt(userArn, JWT_SECRET)

        return {
            "statusCode": 200,
            "body": json.dumps({"jwt": token})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error generating token: {str(e)}")
        }
    
def validate_websocket_jwt(token):
    try:
        decoded = validate_jwt(token, JWT_SECRET)
        return {
            "isAuthorized": True,
            "context": {
                "user": decoded["sub"]
            }
        }
    except ExpiredSignatureError:
        return {
            "isAuthorized": False,
            "statusCode": 403,
            "body": "Token has expired."
        }
    except InvalidTokenError:
        return {
            "isAuthorized": False,
            "statusCode": 403,
            "body": "Invalid token."
        }
