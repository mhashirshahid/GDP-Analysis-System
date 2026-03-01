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

    def execute(self, raw_data: List[Any]) -> None:
        cleaned = self._clean(raw_data)

        self.sink.write(self._top_10(cleaned))
        self.sink.write(self._bottom_10(cleaned))
        self.sink.write(self._growth_rates(cleaned))
        self.sink.write(self._avg_by_continent(cleaned))
        self.sink.write(self._global_trend(cleaned))
        self.sink.write(self._fastest_growing(cleaned))
        self.sink.write(self._consistent_decline(cleaned))
        self.sink.write(self._continent_contribution(cleaned))

    def _clean(self, raw_data : List[dict]) -> List[dict]:
        is_valid = lambda row: (
            row.get('Country Name') and
            row.get('Continent') and
            isinstance(row.get('Continent'), str)
        )
        return list(filter(is_valid, raw_data))
    
    def _top_10(self, data: List[dict]) -> List[dict]:
        filtered = list(filter(
                    lambda row: row.get('Continent') == self.continent and row.get(str(self.year)) is not None,
                    data
        ))
        to_record = lambda row: {
            '_chart_type': 'top_bottom_gdp',
            '_title': f'Top 10 Countries by GDP - {self.continent} ({self.year})',
            'country':     row.get('Country Name'),
            'gdp':         row.get(str(self.year)),
            'rank_label':  'TOP'
    }
        records = list(map(to_record, filtered))
        sorted_records = sorted(records, key=lambda x: x['gdp'], reverse=True)
        return sorted_records[:10]
    
    def _bottom_10(self, data: List[dict]) -> List[dict]:
        filtered = list(filter(
                    lambda row: row.get('Continent') == self.continent and row.get(str(self.year)) is not None,
                    data
            ))
        to_record = lambda row: {
            '_chart_type': 'top_bottom_gdp',
            '_title': f'Bottom 10 Countries by GDP — {self.continent} ({self.year})',
            'country':    row.get('Country Name'),
            'gdp':        row.get(str(self.year)),
            'rank_label': 'BOTTOM'
        }

        records = list(map(to_record, filtered))
        sorted_records = sorted(records, key=lambda x: x['gdp'])
        return sorted_records[:10]
    
    
    
