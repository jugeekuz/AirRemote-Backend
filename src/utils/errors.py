class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ResponseError(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidRequestError(Exception):
    def __init__(self, message):
        super().__init__(message)