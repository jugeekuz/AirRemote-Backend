import re
import ast
from typing import Tuple
from datetime import datetime
from .mixins import BaseValidator

class AutomationsValidator(BaseValidator):

    def check_automation_id(self, automation_id: str):
        
        if not isinstance(automation_id, str):
            return False
        
        return True
      
    def check_automation_name(self, automation_name: str):
        '''
        Method that checks if given argument is str and valid automation name
        '''
        if not isinstance(automation_name, str):
            return False
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, automation_name)
    

    def check_button_name(self, button_name: str):
        '''
        Method that checks if given argument is str and valid button name
        '''
        if not isinstance(button_name, str):
            return False
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, button_name)
    

    def check_remote_name(self, remote_name: str):
        '''
        Method that checks if given argument is str and valid remote name
        '''
        if not isinstance(remote_name, str):
            return False
        pattern = '^[a-zA-Z0-9- ]+$'

        return re.match(pattern, remote_name)


    def check_buttons_list(self, buttons_list: list):
        '''
        Method that checks if given argument is list and valid buttons list
        '''
        if not isinstance(buttons_list, list):
            return False

        required_keys = ["buttonName", "remoteName"]
        for item in buttons_list:

            if not isinstance(item, dict):
                return False
            
            if len(required_keys)!=len(item):
                return False
            
            if not all(attr in item for attr in required_keys):
                return False
            
            if not self.check_button_name(item["buttonName"]):
                return False

            if not self.check_remote_name(item["remoteName"]):
                return False

        return True


    def check_timestamp(self, timestamp: str):

        if not isinstance(timestamp, str):
            return False
        
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            return False
        
        return True
    

    def check_executed_counter(self, executed_counter: str):

        if not isinstance(executed_counter, str):
            return False
        
        try:
            int(executed_counter)
        except ValueError:
            return False

        return True
    
    def check_total_buttons(self, total_buttons: str):
        
        if not isinstance(total_buttons, str):
            return False
        
        try:
            int(total_buttons)
        except ValueError:
            return False

        return True
    
    def check_error_message(self, message: str):

        if not isinstance(message, str):
            return False
        
        return True

    def check_run_error(self, error: str):

        if not isinstance(error, str):
            return False
        
        if not isinstance(eval(error), bool):
            return False
        
        return True
    
    def check_state(self, state: str):

        if not isinstance(state, str):
            return False
        
        if not state in ["ENABLED", "DISABLED"]:
            return False
        
        return True
    
    def check_automation_hour(self, hour: str):
        
        if not isinstance(hour, str):
            return False
        
        try:
            if int(hour) > 23 or int(hour) < 0:
                return False
        except:
            return False
        
        return True
    
    def check_automation_minutes(self, minutes: str):
        
        if not isinstance(minutes, str):
            return False
        
        try:
            if int(minutes) > 59 or int(minutes) < 0:
                return False
        except:
            return False
        
        return True
        
    def check_automation_days(self, days: str):
        
        if not isinstance(days, str):
            return False
        
        try:
            exploded_days = re.split(r'[,-]', days)

            for day in exploded_days:
                if int(day) > 7 or int(day) < 0:
                    return False
        except:
            return False
        
        return True

    def validate(self, items: dict, params: list):
        check_attributes = {
            'automationId': self.check_automation_id,
            'automationName': self.check_automation_name,
            "automationHour": self.check_automation_hour,
            "automationMinutes": self.check_automation_minutes,
            "automationDays": self.check_automation_days,
            'buttonsList': self.check_buttons_list,
            'lastTimestamp': self.check_timestamp,
            'executedCounter': self.check_executed_counter,
            'totalButtons': self.check_button_name,
            'errorMessage': self.check_error_message,
            'automationState': self.check_state,
            'runError': self.check_run_error
        }
        super().validate(check_attributes, items, params=params)


