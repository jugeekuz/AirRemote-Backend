import json
import re
from ...models import RequestPoolModel, RemotesModel
from .mixins.validator_mixin import BaseRequestValidator
from ...utils.errors import InvalidRequestError

class ErrorValidator(BaseRequestValidator):
    def __init__(self, requestpool_model: RequestPoolModel):
        self.requestpool_model = requestpool_model
        super().__init__()

    def validate_error_message(self, request: dict):

        allowed_attributes = ["action", "requestId", "body"]

        self.check_request(request, allowed_attributes)

        requestpool_response = self.requestpool_model.get_requests({"requestId": request["requestId"]})

        if requestpool_response['statusCode']==404 or requestpool_response['statusCode']==500:
            raise InvalidRequestError('RequestId does not exist.')
