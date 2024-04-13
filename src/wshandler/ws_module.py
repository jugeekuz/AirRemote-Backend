import json
class WebSocket:
    '''
    Class meant to handle WebSocket connections
    '''
    def __init__(self, dynamo_db, api_gateway, clients_table):
        self.dynamo_db = dynamo_db
        self.api_gateway = api_gateway
        self.clients_table = clients_table
    
    def connect(self, connection_id: str):
        '''
        Function saving the given `connection_id` to the specified table.
        :param connection_id: Connection Id to save to Dynamo DB table
        :return: 200 response to send or Error 
        '''
        try:
            response = self.dynamo_db.put_item(
                TableName=self.clients_table,
                Item={
                    'connectionId': {'S': connection_id}
                }
            )
            status_code = response['ResponseMetadata'].get('HTTPStatusCode')

            return {"statusCode": status_code,
                    "body": "OK"}
            

        except Exception as e:
            print(f"Unexpected error occured: {e}")
            return
    
    def disconnect(self, connection_id: str):
        '''
        Function deleting the given `connection_id` from the specified table.
        :param connection_id: Connection Id to remove from Dynamo DB table
        :return: 200 response to send or Error 
        '''
        try:
            response = self.dynamo_db.delete_item(
                TableName=self.clients_table,
                Key={
                    'connectionId': {'S': connection_id}
                    }
            )
            status_code = response['ResponseMetadata'].get('HTTPStatusCode')

            return {"statusCode": status_code,
                    "body": "OK"}
        except Exception as e:
            print(e)
            return

    def send_message(self, connection_id: str, body: dict):
        '''
        Function sending `body` through api_gateway to given `connection_id`.
        :param connection_id: Connection Id to send the message
        :param body: Message to send
        '''
        try:
            response = self.api_gateway.post_to_connection(
                Data = json.dumps(body),
                ConnectionId = connection_id
            )
            status_code = response['ResponseMetadata'].get('HTTPStatusCode')
            return {"statusCode": status_code,
                    "body": "OK"}
        except Exception as e:
            print(e)
            return

    def send_message_all(self, this_connection_id: str, body: dict):
        '''
        Function sending `body` to all connections, except `this_connection_id`.
        :param this_connection_id: Connection Id sending the message
        :param body: Message to send
        :return: 200 response code or error
        '''
        try:
            output = self.dynamo_db.scan(
                TableName=self.clients_table
            )

            if not output['Items']:
                return

            for item in output['Items']:
                if item["connectionId"]['S'] != this_connection_id:
                    self.send_message(item["connectionId"]['S'], body)

            return {"statusCode": 200,
                    "body": "OK"}
        except Exception as e:
            print(e)
            return