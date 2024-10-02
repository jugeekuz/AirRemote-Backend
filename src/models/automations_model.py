import re
import random
import string
from datetime import datetime, timedelta
from .mixins import ObjectDynamodb
from .validators import AutomationsValidator
from ..utils.helpers import error_handler, check_response
from ..utils.errors import ResponseError

class AutomationsModel(ObjectDynamodb):
    '''
    Class used to handle clients.
    This class provides capability to store, retrieve, update and delete clients from AWS DynamoDB.
    '''
    def __init__(self, clients_table: str):

        self.validator = AutomationsValidator()

        super().__init__(clients_table)
        
    def get_automations(self):

        self.clean_expired_automations()

        return self.scan_items()

    @error_handler
    def get_automation(self, key: dict):

        self.validator.validate(key, params=['automationId'])

        return self.get_item(key)
    
    @error_handler
    def add_automation(self, automation: dict):

        time = datetime.now()

        automation_id = ''.join(random.choices(string.ascii_letters + string.digits, k=3)) + '_' + str(time.timestamp())        

        attributes = {
                        "automationId": automation_id,
                        "lastTimestamp": time.isoformat(),
                        "executedCounter": "0",
                        "totalButtons": str(len(automation['buttonsList'])),
                        "errorMessage": "",
                        "runError": "False",
                        "automationState": "ENABLED"
                     }
        automation = { 
                        **automation, 
                        **attributes,
                      }

        self.validator.validate(automation, params=["automationId",
                                                    "automationName",
                                                    "automationHour",
                                                    "automationMinutes",
                                                    "automationDays",
                                                    "buttonsList",
                                                    "lastTimestamp",
                                                    "executedCounter",
                                                    "totalButtons",
                                                    "errorMessage",
                                                    "runError",
                                                    "automationState"
                                                    ])

        response = self.add_item(automation)

        if response['statusCode'] == 201:      
            response['body'] = {'automationId' : automation_id}
        
        return response
    
    @error_handler
    def delete_automation(self, key: dict):

        self.validator.validate(key, params=['automationId'])
        
        return self.delete_item(key)
    
    @error_handler
    def set_automation_state(self, key: dict, state: str):
        
        self.validator.validate({**key, "automationState": state}, ['automationId',
                                                                    'automationState'])

        return self.update_item(key, {"automationState": state})

    @error_handler
    def increment_counter(self, key: dict):

        self.validator.validate(key, params=['automationId'])

        automations_response = self.get_automation(key)

        time = datetime.now()

        if not check_response(automations_response):
            return automations_response

        counter = int(automations_response['body']['executedCounter'])
        totalButtons = int(automations_response['body']['totalButtons'])

        if counter == totalButtons - 1:
            self.update_item(key, { "executedCounter": '0',
                                    "lastTimestamp": time.isoformat(),
                                    "errorMessage": "",
                                    "runError": "False" })
            return {"statusCode": 200,
                    "body": "Automation Finished"} 

        return self.update_item(key, { "executedCounter": f"{counter + 1}",
                                       "lastTimestamp": time.isoformat() })
    
    @error_handler
    def set_error_message(self, key: dict, message: str):
        
        entry = {"errorMessage": message,
                "runError": "True"}
        
        if not message:
            entry = {"errorMessage": "",
                     "runError": "False"}

        self.validator.validate({**entry , **key}, params=['automationId', 'runError', 'errorMessage'])

        return self.update_item(key, entry)
            
    
    @error_handler
    def clean_expired_automations(self):

        expired_automations = []

        automations_response = self.get_automations()

        time = datetime.now()

        if not check_response(automations_response):
            return automations_response

        for automation in automations_response["body"]:
            automation_time = datetime.fromisoformat(automation['lastTimestamp'])
            if (datetime.now() - automation_time > timedelta(seconds=40)) and int(automation["executedCounter"]) != 0:
                expired_automations.append({"automationId": automation["automationId"]})


        for key in expired_automations:
            _ = self.update_item(key, { "executedCounter": '0',
                                        "lastTimestamp": time.isoformat(),
                                        "errorMessage": "Unexpected error. Automation didn't manage to run successfully.",
                                        "runError": "True"})

        return {"statusCode": 200,
                "body": "Successfully cleaned requests."}
