from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

def serialize_item(dict: dict):
    '''
    Function used to serialize data in appropriate format for DynamoDB.
    :param dict `dict`: The item to serialize.
    :return : Item in format appropriate for dynamodb.
    '''
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in dict.items()
    }

def serialize_items(list: list):
    '''
    Function used to serialize a list of data in appropriate format for DynamoDB.
    :param list `list`: The list of items to serialize.
    :return : List of items in format appropriate for dynamodb.
    '''
    return [serialize_item(item) for item in list]


def deserialize_item(dynamo_obj: dict):
    '''
    Function used to deserialize data from DynamoDB format to Python dictionary.
    :param dict `dynamo_obj`: The item to deserialize.
    :return : Item in python dict format.
    '''
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    } 

def deserialize_items(dynamo_obj_list: list):
    '''
    Function used to deserialize a list of data from DynamoDB format to Python dictionary.
    :param list `dynamo_obj_list`: A list of items in DynamoDB format to be deserialized.
    :return : List of items in python dict format.
    '''
    return [deserialize_item(item) for item in dynamo_obj_list]

def check_response(response: dict):
    '''
    Function used to check if the status code of the response is in 2xx form and if body isn't empty.
    :param dict `response`: The response to check
    :returns : True if response is in form 2xx and the body isn't empty, False otherwise.
    '''
    status_code = str(response["statusCode"])
    if status_code.startswith('2') and response["body"]:
        return True
    return False

def error_handler(func):
    '''
    Decorator used to wrap a function in a try catch block and return a 500 response with the error in body if thrown.
    '''
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {"statusCode": 500,
                    "body": f"Received unexpected error in `{func.__name__}` : {e}"}
    return wrapper