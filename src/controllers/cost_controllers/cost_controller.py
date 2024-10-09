import json
import datetime
import boto3
from ...utils.helpers import check_response

def get_monthly_cost():
    client = boto3.client('ce')

    today = datetime.date.today()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    
    total_cost = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']

    return {
        'statusCode': 200,
        'body': {"totalCost": total_cost} 
    }