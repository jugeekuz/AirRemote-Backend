import boto3.dynamodb.conditions as conditions
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

class ObjectDynamodb:
    def __init__(self, dynamo_db, table):
        self.dynamo_db = dynamo_db
        self.table = table

    def _deserialize_item(self, dynamo_obj: dict):
        deserializer = TypeDeserializer()
        return {
            k: deserializer.deserialize(v) 
            for k, v in dynamo_obj.items()
        } 
    def _deserialize_items(self, dynamo_obj_list: list):
        return [self._deserialize_dynamodb_item(item) for item in dynamo_obj_list]
    
    def _serialize_item(self, dict: dict):
        return
    
    def _serialize_items(self, list: list):
        return
    
    def _error(self, e):
       return {"statusCode": 500,
               "body": f"Received unexpected error: {e}"}

    def get_items(self):
        try:
            response = self.dynamo_db.scan(
                TableName=self.table
            )
            result = self._deserialize_dynamodb_items(response["Items"])
            return {"statusCode": 200,
                    "body": result}
        except Exception as e:
            return self._error(e)

    def get_item(self, key: dict):
        try:
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
                
        except Exception as e:
           return self._error(e)
        

    def add_item(self, item: dict):
        try:
            item = self._serialize_item(item)
            response = self.dynamo_db.put_item(
                TableName=self.table,
                Item=item
            )
            return {"statusCode": 201,
                    "body": "created"} 
        
        except Exception as e:
           return self._error(e)


    def delete_item(self,item: dict):
        try:
            item = self._serialize_item(item)
            response = self.dynamo_db.delete_item(
                TableName=self.table,
                Key=item
            )
            return {"statusCode": 200,
                    "body": "deleted"}
        
        except Exception as e:
           return self._error(e)

    
    def append_to_list(self, key: dict, list_name: str, item: dict,):
        try:
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
        
        except Exception as e:
            return self._error(e)