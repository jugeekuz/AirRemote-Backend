import boto3.dynamodb.conditions as conditions

class Remote:
    '''
    Class used to handle remote control commands.
    '''
    def __init__(self, dynamo_db, api_gateway, remotes_table):
        self.dynamo_db = dynamo_db
        self.api_gateway = api_gateway
        self.remotes_table = remotes_table

    def get_all_remotes(self):
        try:
            result = self.dynamo_db.scan(
                TableName=self.remotes_table
            )
            return {"statusCode": 200,
                    "body": result["Items"]}
        except Exception as e:
            print(e) 
            return

    def add_remote(self, remote_name: str, protocol: str, command_size: str):
        '''
        Function used to save remotes to Dynamo DB
        :param remote_name: Name of the remote control to be saved.
        :param protocol: IR transmission protocol used by appliance using this remote.
        :param command_size: Size of the commands used.
        return:
        '''
        try:
            response = self.dynamo_db.put_item(
                TableName=self.remotes_table,
                Item={
                    'remoteName': {'S': remote_name},
                    'protocol': {'S': protocol},
                    'commandSize': {'S': command_size},
                    'buttons': {'L': []}
                }
            )
            return {"statusCode": 201,
                    "body": "created"} 
        
        except Exception as e:
            print(e)
            return

    def delete_remote(self, remote_name: str):
        '''
        Function used to delete remotes from Dynamo DB
        :param remote_name: Name of the remote control to be deleted.
        return:
        '''
        try:
            response = self.dynamo_db.delete_item(
                TableName=self.remotes_table,
                Key={
                    'remoteName': {'S': remote_name}
                }
            )
            return {"statusCode": 200,
                    "body": "deleted"}
        except Exception as e:
            print(e)
            return

    def add_button(self, remote_name: str, button_name: str, button_code: str):
        '''
        Function used to add buttons to saved remotes in Dynamo DB
        :param remote_name: Name of the remote control to be updated.
        :param button_name: Name of the button to be saved.
        :param button_code: Hex Code of the command to be saved.
        return:
        '''
        try:
            response = self.dynamo_db.update_item(
                TableName=self.remotes_table,
                Key={
                    'remoteName': {'S': remote_name}
                },
                UpdateExpression='SET #b = list_append(#b, :button)',
                ExpressionAttributeNames={
                    "#b": "buttons",
                },
                ExpressionAttributeValues={
                    ":button": {'L': [
                                    {'M': {
                                        'buttonName': {'S': button_name},
                                        'buttonCode': {'S': button_code}
                                        }
                                    }]     
                    },
                },
                ReturnValues="UPDATED_NEW"
            )
            return {"statusCode": 200,
                    "body": "updated"} 
        except Exception as e:
            print(e)
            return {"statusCode": 400,
                    "body": e}
     
    def get_remote(self, remote_name: str):
        try:
            result = self.dynamo_db.get_item(
                TableName=self.remotes_table,
                Key={
                    'remoteName': {'S': remote_name}
                }
            )
            if 'Item' in result:
                return {"statusCode": 200,
                        "body": result["Item"]}
            else:
                return {"statusCode": 404,
                        "body": "Item not found"}
        except Exception as e:
            print(e) 
            return
        
    def get_button(self, remote: dict, button_name: str):
        raise NotImplementedError

    def handle_command(self, body):
        match body['command']:
            case "getRemotes":
                return self.get_all_remotes()
            case "getRemote":
                remote = body["remote"]
                return self.get_remote(remote["remoteName"])
            case "addRemote":
                remote = body["remote"]
                return self.add_remote(remote["remoteName"], remote["protocol"], remote["commandSize"])
            case "addButton":
                remote = body["remote"]
                button = body["button"]
                return self.add_button(remote["remoteName"], button["buttonName"], button["buttonCode"])
            case "deleteRemote":
                remote = body["remote"]
                return self.delete_remote(remote["remoteName"])
            case _:
                return {
                    "statusCode": 400,
                    "body": "Bad Request"
                }
                raise NotImplementedError

        return body