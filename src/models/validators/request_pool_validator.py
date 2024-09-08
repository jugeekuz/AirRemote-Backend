import re
import json
from datetime import datetime
from .mixins import BaseValidator

class RequestPoolValidator(BaseValidator):
    def check_request_id(self, id: str):

        return isinstance(id, str)
        
    
    def check_timestamp(self, timestamp: str):

        if not isinstance(timestamp, str):
            return False
        
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            return False
        
        return True
    
    def check_connection_id(self, key: str):
        '''
        Checks if `key` is in valid format by being `str` and in Base64 format.
        '''
        if not isinstance(key, str):
            return False

        if len(key)%4 != 0:
            return False
        
        if not re.match(r'^[A-Za-z0-9+/_\-]+={0,2}$', key):
            return False
        
        return True

    def check_request(self, body: str):

        if not isinstance(body, str):
            return False
        
        try:
            request = json.loads(body)
        except:
            return False
        
        return True

    def validate(self, items: dict, params: list):
        check_attributes = {
            'requestId': self.check_request_id,
            'timestamp': self.check_timestamp,
            'connectionId': self.check_connection_id,
            'requestBody': self.check_request
        }
        super().validate(check_attributes, items, params=params)


    