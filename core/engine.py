from typing import List,Any
from core.contracts import DataSink

class TransformationEngine:
    def __init__ (self, sink: DataSink, config: dict):
        self.sink = sink
        filters = config.get('filters',{})
        self.continent = filters.get('continent', 'Asia')
        self.year = filters.get('year', 2019)
        self.year_start = filters.get('year_range', [2010, 2023])[0]
        self.year_end = filters.get('year_range', [2010, 2023])[1]
        self.decline_years = filters.get('decline_years', 5)
