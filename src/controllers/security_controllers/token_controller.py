from .utils import generate_token, generate_salt, hash_token
import json
def get_device_token():
    return {
        'statusCode': 200,
        'body': {
            'deviceToken': generate_token()
        }
    }