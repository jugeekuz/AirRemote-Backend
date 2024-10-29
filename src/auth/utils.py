import json
import os

CORS_ORIGIN = os.getenv('CORS_ORIGIN')

def send_response(status_code, body):
    response = {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            "Access-Control-Allow-Credentials": 'true'
        }
    }
    return response

def validate_input(data):
    try:
        body = json.loads(data)
        email = body.get('email')
        password = body.get('password')
        if not email or not password or len(password) < 6:
            return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False
