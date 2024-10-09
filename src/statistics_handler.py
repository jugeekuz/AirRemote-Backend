import os
from .models import StatisticsModel
from .controllers.cost_controllers.cost_controller import get_monthly_cost
from .utils.helpers import check_response

def handle(event, context):
    '''
    Since AWS Cost Explorer API is really expensive per request, 
    an EventBridge schedule will calculate cost at the end of each month and save it to DynamoDB.
    '''
    STATISTICS_TABLE= os.getenv("STATISTICS_TABLE_NAME", "")
    
    statistics = StatisticsModel(STATISTICS_TABLE)

    statistics_response = statistics.get_statistics()
    
    cost_response = get_monthly_cost()
    
    if len(statistics_response['body']) == 0:
        return statistics.initialize_statistics(cost_response['body'])

    return statistics.update_statistics(cost_response['body'])