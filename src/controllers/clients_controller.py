from ..models.model_handler import ObjectDynamodb

class WebsocketClients(ObjectDynamodb):

    def __init__(self, dynamo_db,  clients_table):
        self.dynamo_db = dynamo_db
        self.clients_table = clients_table
        super().__init__(dynamo_db, clients_table)


    def handler(self, body):
        raise NotImplementedError

    