from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3.dynamodb.conditions import Attr, And

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {"statusCode": 500,
                    "body": f"Received unexpected error: {e}"}
    return wrapper

class ObjectDynamodb:
    def __init__(self, dynamo_db, table: str):
        self.dynamo_db = dynamo_db
        self.table = table

    def _serialize_item(self, dict: dict):
        '''
        Method used to serialize data in appropriate format for DynamoDB.
        '''
        serializer = TypeSerializer()
        return {
            k: serializer.serialize(v)
            for k, v in dict.items()
        }
    
    def _serialize_items(self, list: list):
        '''
        Method used to serialize a list of data in appropriate format for DynamoDB.
        '''
        return [self._serialize_item(item) for item in list]
    

    def _deserialize_item(self, dynamo_obj: dict):
        '''
        Method used to deserialize data from DynamoDB format to Python dictionary.
        '''
        deserializer = TypeDeserializer()
        return {
            k: deserializer.deserialize(v) 
            for k, v in dynamo_obj.items()
        } 
    def _deserialize_items(self, dynamo_obj_list: list):
        return [self._deserialize_dynamodb_item(item) for item in dynamo_obj_list]
    
    @error_handler
    def get_items(self):
        '''
        Method used to get all items of a given table.
        '''
        response = self.dynamo_db.scan(
            TableName=self.table
        )
        result = self._deserialize_items(response["Items"])
        return {"statusCode": 200,
                "body": result}

    @error_handler
    def get_item(self, key: dict):
        '''
        Method used to get particular item from table specified by a key.
        '''
        key = self._serialize_item(key)
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key=key
        )            

        if (res := self._deserialize_dynamodb_item(response["Item"])):
            return {"statusCode": 200,
                    "body": res}
        
        else:
            return {"statusCode": 404,
                    "body": "Content Not Found"}
    
    @error_handler
    def scan_item(self, item: dict):
        '''
        Method used to get an item that matches all specific key-value pairs in `item`.
        '''
        filter_expressions = [Attr(k).eq(v) for k,v in item.items()]

        response = self.dynamo_db.scan(
            TableName=self.table,
            FilterExpression=And(*filter_expressions)
        )
        return {"statusCode": 200,
                "body": response["Items"]}
    
    @error_handler
    def add_item(self, item: dict):
        '''
        Method used to add an item to the table.
        '''
        item = self._serialize_item(item)
        response = self.dynamo_db.put_item(
            TableName=self.table,
            Item=item
        )
        return {"statusCode": 201,
                "body": "created"} 
        
   
    @error_handler
    def delete_item(self, key: dict):
        '''
        Method used to delete an key from the table specified by key.
        '''
        key = self._serialize_item(key)
        response = self.dynamo_db.delete_item(
            TableName=self.table,
            Key=key
        )
        return {"statusCode": 200,
                "body": "deleted"}
        
    @error_handler
    def update_item(self, key: dict, item: dict):
        '''
        Method used to update all columns of an item specified by `key` to the values specified in key-value pairs in `item`.
        '''
        key = self._serialize_item(key)
        update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in item.keys())
        expression_attribute_values = {f":{k}": v for k, v in item.items()}
        response = self.dynamo_db.update_item(
            TableName=self.table,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return {"statusCode": 200,
                "body": "updated"} 

    @error_handler
    def append_to_list(self, key: dict, list_name: str, item: dict):
        '''
        Method used to update an item containing an attribute of List type by appending to that `item` to that list.
        '''
        key = self._serialize_item(key)
        item = self._serialize_item([item])
        response = self.dynamo_db.update_item(
            TableName=self.table,
            Key=key,
            UpdateExpression='SET #b = list_append(#b, :item)',
            ExpressionAttributeNames={
                "#b": list_name,
            },
            ExpressionAttributeValues={
                ":item": item,
            },
            ReturnValues="UPDATED_NEW"
        )
        return {"statusCode": 200,
                "body": "updated"} 