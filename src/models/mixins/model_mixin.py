import boto3
from ...utils.helpers import serialize_item, serialize_items, deserialize_item, deserialize_items, error_handler, check_response, serialize_list, deserialize_list


class ObjectDynamodb:
    '''
    Class used to abstract over certain DynamoDB operations. 
    A DynamoDB resource and a table are passed and the class provides methods to add, get, update items and more.
    '''
    def __init__(self, table: str):
        '''
        :param `dynamo_db`: boto3 DynamoDB resource
        :param str `table`: Name of the table to perform operations on.
        '''
        self.dynamo_db = boto3.client('dynamodb')
        self.table = table


    @error_handler
    def get_item(self, key: dict):
        '''
        Method used to get particular item from `self.table` specified by a key.

        :param dict `key`: The key to search by.
        :return : Response 200 with key in `body` if key exists or Response 404 or Response 500 error.
        '''
        key = serialize_item(key)
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key=key
        )            
        if not "Item" in response or not response["Item"]:
            return {"statusCode": 404,
                    "body": []}
        
        return {"statusCode": 200,
                "body": deserialize_item(response["Item"])}
    
    
    @error_handler
    def scan_items(self, filter: dict = None):
        '''
        Method used to get all items that match all specific key-value pairs in `filter`.

        :param dict `filter`: Key-value pairs to use as filter expressions for items (can be left empty to scan all items).
        :return : Response 200 with list of items that match filtering or Response 500 error.
        '''
        scan_kwargs = {
            'TableName': self.table,
            'Select': 'ALL_ATTRIBUTES'  
        }
        
        if filter:
            filter_expression = ' AND '.join([f"{k} = :{k}" for k in filter.keys()])
            expression_attribute_values = serialize_item({f":{k}": v for k, v in filter.items()})
            
            scan_kwargs['FilterExpression'] = filter_expression
            scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values

        response = self.dynamo_db.scan(**scan_kwargs)

        return {"statusCode": 200,
                "body": deserialize_items(response["Items"])}
    

    @error_handler
    def add_item(self, item: dict):
        '''
        Method used to add  `item` to `self.table`.

        :param dict `item`: The item to add.
        :return : Response 201 or Response 500 error.
        '''
        item = serialize_item(item)
        response = self.dynamo_db.put_item(
            TableName=self.table,
            Item=item
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "statusCode": 201,
                "body": "Item successfully created."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error creating item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }
        
   
    @error_handler
    def delete_item(self, key: dict):
        '''
        Method used to delete an key from `self.table` specified by `key`.

        :param dict `key`: The key of the item to delete.
        :return : Response 200 or Response 500 error.
        '''
        key = serialize_item(key)
        response = self.dynamo_db.delete_item(
            TableName=self.table,
            Key=key
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "statusCode": 200,
                "body": "Item successfully deleted."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error deleting item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }
        
    @error_handler
    def update_item(self, key: dict, new_values: dict):
        '''
        Method used to update an item matching `key` by changing all columns to the values specified by key-value pairs in `new_values`.

        :param dict `key`: Key of the item to update.
        :param dict `new_values`: New values of equivalent columns in key-value pairs.
        :return : Response 200 or Response 500 error.
        '''
        key = serialize_item(key)
        new_values = serialize_item(new_values)
        update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in new_values.keys())
        expression_attribute_values = {f":{k}": v for k, v in new_values.items()}
        response = self.dynamo_db.update_item(
            TableName=self.table,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "statusCode": 201,
                "body": "Item successfully updated."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error updating item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }

    def update_sort_key(self, key: dict, new_item: dict):
        '''
        Method used to update attributes of the table used as a sort key, by first deleting and then placing `new_item` in place of it.
        :param dict `key`: The key of the item to update.
        :param dict `new_item`: The new item to replace it with.
        :return : Response 200 or Response 500 error.
        '''
        transact_items = [
            {
                'Delete': {
                    'TableName': self.table,
                    'Key': key
                }
            },
            {
                'Put': {
                    'TableName': self.table,
                    'Item': new_item
                }
            },
        ]

        response = self.dynamo_db.transact_write_items(
            TransactItems=transact_items
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "statusCode": 201,
                "body": "Item successfully updated."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error updating item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }

    @error_handler
    def append_to_list(self, key: dict, list_name: str, item: dict):
        '''
        Method used to update an item specified by `key` by appending `item` to the list `list_name` attribute.

        :param dict `key`: Key of the item to update.
        :param str `list_name`: Name of the column containing the list to append to.
        :param dict `item`: Item to append to that list.
        :return : Response 200 or Response 500 error.
        '''
        key = serialize_item(key)
        item = serialize_item(item)
        response = self.dynamo_db.update_item(
            TableName=self.table,
            Key=key,
            UpdateExpression='SET #b = list_append(#b, :item)',
            ExpressionAttributeNames={
                "#b": list_name,
            },
            ExpressionAttributeValues={
                ":item": {'L': [{'M': item}]},
            },
            ReturnValues="UPDATED_NEW"
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "statusCode": 201,
                "body": "Item successfully updated."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error updating item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }
    
    @error_handler
    def delete_from_list(self, key: dict, list_name: str, item: dict):
        '''
        Method used to delete an object from a list of objects, if `item` exists within that object.

        :param dict `key`: Key of the item to update.
        :param str `list_name`: Name of the column containing the list to delete from.
        :param dict `item`: Item to delete from `list_name`.
        :return : Response 200 or Response 500 error.
        '''
        key = serialize_item(key)
        
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key=key
        )            
        if not "Item" in response or not response["Item"]:
            return {"statusCode": 404,
                    "body": []}        
        
        obj_list = deserialize_list(response['Item'][list_name])

        is_subset = lambda subset, superset: all(subset_key in superset and superset[subset_key].strip() == subset_value.strip() for subset_key, subset_value in subset.items())

        new_obj_list = serialize_list([obj for obj in obj_list if not is_subset(item, obj)])
        
        response = self.dynamo_db.update_item(
            TableName=self.table,
            Key=key,
            UpdateExpression='SET #lst = :val',
            ExpressionAttributeNames={
                "#lst": list_name,
            },
            ExpressionAttributeValues={
                ':val': new_obj_list
            }
        )
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "statusCode": 200,
                "body": "Item successfully deleted."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error deleting item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }