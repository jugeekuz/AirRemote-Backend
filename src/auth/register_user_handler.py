import json
import os
from .utils import send_response
from ..models import RegisteredUsersModel
USERS_MODEL = os.getenv('REGISTERED_USERS_TABLE_NAME')
CORS_ORIGIN = os.getenv('CORS_ORIGIN')
def handle(event, context):
    try:
        body = json.loads(event['body'])
        user_email = body.get('userEmail')
        
        if not user_email:
            return send_response(400, {'message': 'Invalid input'})
        
        users = RegisteredUsersModel(USERS_MODEL)
        response = users.add_user({"userEmail": user_email})

        if response['statusCode'] != 201:
            return send_response(400, {'message': 'User already exists'})
        
        return send_response(200, {'message': 'User added succesfully'})
    
    except Exception as error:
        message = str(error) if str(error) else 'Internal server error'
        return send_response(500, {'message': message})