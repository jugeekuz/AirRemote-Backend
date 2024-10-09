import re
import json
from datetime import datetime
from .mixins import BaseValidator

class StatisticsValidator(BaseValidator):

    def check_total_cost(self, cost: str):

        if not isinstance(cost, str):
            return False
        
        try:
            if float(cost) < 0 :
                return False
        except:
            return False
        
        return True
    
    def check_statistics_id(self, id: str):
        if not isinstance(id, str):
            return False
        
        if id != "STATISTICS_ID":
            return False
        
        return True

    def validate(self, items: dict, params: list):
        check_attributes = {
            'totalCost': self.check_total_cost,
            'statisticsId': self.check_statistics_id
        }
        super().validate(check_attributes, items, params=params)


    