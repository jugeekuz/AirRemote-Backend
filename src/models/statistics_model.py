from .mixins import ObjectDynamodb
from .validators import StatisticsValidator
from ..utils.helpers import error_handler, check_response
from ..utils.errors import ResponseError

class StatisticsModel(ObjectDynamodb):
    def __init__(self, statistics_table: str):

        self.validator = StatisticsValidator()

        super().__init__(statistics_table)

    @error_handler
    def get_statistics(self):
        return self.scan_items()
    
    @error_handler
    def initialize_statistics(self, total_cost: dict):
        item = {
            'statisticsId': 'STATISTICS_ID',
            **total_cost
        }
        self.validator.validate(item, params=['statisticsId',
                                              'totalCost'])
        return self.add_item(item)

    @error_handler
    def update_statistics(self, statistics: dict):
        
        key = { 'statisticsId': 'STATISTICS_ID' }

        self.validator.validate({**key, **statistics}, params= ['statisticsId',
                                                                'totalCost'])

        return self.update_item(key, statistics)