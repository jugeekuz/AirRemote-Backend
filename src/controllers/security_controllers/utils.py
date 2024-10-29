import os
import hashlib
import base64

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