import json
import random
import string
from datetime import datetime, timedelta
from .mixins import ObjectDynamodb
from .validators import RequestPoolValidator
from ..utils.helpers import check_response, error_handler

class RequestPoolModel(ObjectDynamodb):
    def __init__(self, request_pool_table: str):

        self.validator = RequestPoolValidator()

        super().__init__(request_pool_table)

    @error_handler
    def add_request(self, connection_id: str, request: dict):
        
        time = datetime.now()

        request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=3)) + '_' + str(time.timestamp())

        request_body = json.dumps(request)
    
        item = {
            "requestId": request_id,
            "timestamp": time.isoformat(),
            "connectionId": connection_id,
            "requestBody": request_body
        }

        self.validator.validate(item, ['requestId',
                                       'connectionId',
                                       'timestamp',
                                       'requestBody'])
        
        response = self.add_item(item)

        if response["statusCode"] == 201:
            response["body"] = {"requestId": request_id}

        return response
        
    @error_handler
    def get_requests(self, request: dict = None):

        if request:
            self.validator.validate(request, ['requestId'])

            return self.get_item(request)
        
        return self.scan_items()
    
    @error_handler
    def delete_request(self, request: dict):

        self.validator.validate(request, ['requestId'])

        return self.delete_item(request)
    
    @error_handler
    def clean_expired_requests(self):

        expired_requests = []

        requests_response = self.get_requests()

        if not check_response(requests_response):
            return requests_response

        for request in requests_response["body"]:
            request_time = datetime.fromisoformat(request['timestamp'])
            if datetime.now() - request_time > timedelta(seconds=40):
                expired_requests.append(request)


        for request in expired_requests:
            delete_response = self.delete_request({"requestId": request['requestId']})

        return {"statusCode": 200,
                "body": "Successfully cleaned requests."}