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
    @error_handler
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
        
    @error_handler
    def rearrange_items(self, indices_list: list, primary_key_field: str):
        '''
        Function that takes as input a list of indices and rearranges the order of items in the table,
        changing the `orderIndex` fields to new values by performing batch write.
        :param list `indices_list`: List of indices representing new order of items.
        :param str `primary_key_field`: Primary key name of the table.
        :return : Response 200 or Response 500 error.
        '''

        response = self.scan_items()

        if not check_response(response):
            return {
                "statusCode": 500,
                "body": "Error while retrieving items."
            }

        items = response['body']

        if 'orderIndex' not in items[0]:
            return {
                "statusCode": 400,
                "body": "Table is not sortable."
            }

        if len(items) != len(indices_list) or set(indices_list) != set(range(0,len(items))):
            return {
                "statusCode": 400,
                "body": "Indices list is invalid."
            }
        indices_list = [str(item) for item in indices_list]

        items_to_update = []
        for item, new_order_index in zip(items, indices_list):
            if item['orderIndex'] == new_order_index:
                continue
            item_to_update = {
                "Key": {primary_key_field: item[primary_key_field]},
                "Item": {":orderIndex": new_order_index},
            }
            items_to_update.append(item_to_update)
        
        if len(items_to_update) == 0:
            return {
                "statusCode": 400,
                "body": "Invalid request, no items to rearrange."
            }
        transaction_items = [
            {
                'Update': {
                    'TableName': self.table,
                    'Key': serialize_item(item["Key"]),
                    'UpdateExpression': "SET orderIndex = :orderIndex",
                    'ExpressionAttributeValues': serialize_item(item["Item"]),
                }
            }
            for item in items_to_update
        ]
        
        response = self.dynamo_db.transact_write_items(
            TransactItems=transaction_items
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {
                "statusCode": 200,
                "body": "Items rearranged successfully."
            }
        else :
            return {
                "statusCode": 500,
                "body": "Unexpected error while rearranging items."
            }


    @error_handler
    def rearrange_list(self, key: dict, list_name: str, new_order: list):
        key = serialize_item(key)
        
        response = self.dynamo_db.get_item(
            TableName=self.table,
            Key=key
        )            
        if not "Item" in response or not response["Item"]:
            return {"statusCode": 404,
                    "body": []}        
        
        items = deserialize_list(response['Item'][list_name])

        if len(items) != len(new_order) or set(new_order) != set(range(0,len(items))):
            return {
                "statusCode": 400,
                "body": "Indices list is invalid."
            }
        
        new_list = [items[i] for i in new_order]
        
        new_obj_list = serialize_list(new_list)

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
                "body": "List Successfully Rearranged."
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error rearranging item. DynamoDB returned status code {response['ResponseMetadata']['HTTPStatusCode']}."
            }
    
    @error_handler
    def clean_order_indexes(self, primary_key_field: str):
        '''
        If we delete an item the middle item on a list w/ order indexes [0,1,2], then the order indexes of the list will be [0,2].
        This method cleans the list so there are no gaps in between.
        '''
        response = self.scan_items()

        if not check_response(response):
            return {
                "statusCode": 500,
                "body": "Error while retrieving items."
            }

        items = response['body']

        if 'orderIndex' not in items[0]:
            return {
                "statusCode": 400,
                "body": "Table is not sortable."
            }

        order_indexes = [int(item['orderIndex']) for item in items]

        if set(order_indexes) == set(range(0,len(items))):
            return {
                "statusCode": 400,
                "body": "Nothing to clean. Order Indexes are valid."
            }
        
        sorted_indexes = order_indexes.copy()
        sorted_indexes.sort()

        # The sorted order indexes now contains a mapping from old value (sorted_indexes[i]) to new value -> (i)
        # To make the process more efficient we will create a hashmap mapping old indexes -> new indexes
        # Such that indexes_mapping[old_index] == new_index
        indexes_mapping = [-1]*(max(sorted_indexes)+1)
        for (i,old_idx) in enumerate(sorted_indexes):
            indexes_mapping[old_idx] = i
            # if indexes_mapping[3] = 1 it means that the index 3 is now the second index in the list
            # if indexes_mapping[i] == -1 it means that i doesnt exist

        items_to_update = []
        for (i, item) in enumerate(items):
            old_index = int(item['orderIndex'])
            new_index = indexes_mapping[old_index]

            if old_index == new_index:
                continue

            item_to_update = {
                "Key": {primary_key_field: item[primary_key_field]},
                "Item": {":orderIndex": str(new_index)},
            }
            items_to_update.append(item_to_update)
        
        if len(items_to_update) == 0:
            return {
                "statusCode": 400,
                "body": "Invalid request, no items to rearrange."
            }
        

        transaction_items = [
            {
                'Update': {
                    'TableName': self.table,
                    'Key': serialize_item(item["Key"]),
                    'UpdateExpression': "SET orderIndex = :orderIndex",
                    'ExpressionAttributeValues': serialize_item(item["Item"]),
                }
            }
            for item in items_to_update
        ]
        
        response = self.dynamo_db.transact_write_items(
            TransactItems=transaction_items
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {
                "statusCode": 200,
                "body": "Items cleaned successfully."
            }
        else :
            return {
                "statusCode": 500,
                "body": "Unexpected error while cleaning items."
            }