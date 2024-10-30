import os
import sys
sys.path.insert(0, 'src/vendor')
import json
import base64
import hashlib
import datetime
import jwt

def generate_token(length=32):
    """Generates a cryptographically secure random token."""
    token = base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')
    return token

def generate_salt(length=16):
    """Generates a random salt."""
    salt = base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')
    return salt

def hash_token(token, salt):
    """Hashes the token with the salt using SHA-256."""
    # Concatenate token and salt
    token_salt = token + salt
    
    # Hash the concatenated value
    hash_object = hashlib.sha256(token_salt.encode('utf-8'))
    token_hash = hash_object.hexdigest()
    
    return token_hash

def generate_jwt(sub, secret, expiry_minutes=1):
    """Generates JWT to be provided to frontend for authorizing Websocket Requests"""
    payload = {
        "sub": sub,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)  
    }
    return jwt.encode(payload, secret, algorithm="HS256")
    
def validate_jwt(token, secret):

    return jwt.decode(token, secret, algorithms=["HS256"])
    