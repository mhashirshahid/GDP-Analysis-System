from typing import List,Any
from core.contracts import DataSink
from itertools import chain
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
    
    def _growth_rates(self, data: List[dict]) -> List[dict]:
        continent_data = list(filter(
        lambda row: row.get('Continent') == self.continent,
        data
        ))

        countries = list(set(map(
        lambda row: row.get('Country Name'),
        continent_data
        )))

        def calc_growth(country):
            country_rows = list(filter(
            lambda r: r.get('Country Name') == country,
            continent_data
        ))

            year_gdp_pairs = list(filter(
            lambda pair: pair[1] is not None,
            map(lambda yr: (yr, country_rows[0].get(str(yr))),
                range(self.year_start, self.year_end + 1))
            ))

            if len(year_gdp_pairs) < 2:
                return None

            first_gdp = year_gdp_pairs[0][1]
            last_gdp  = year_gdp_pairs[-1][1]

            if first_gdp == 0 or first_gdp is None:
                return None

            rate = ((last_gdp - first_gdp) / first_gdp) * 100

            return {
            '_chart_type': 'gdp_growth_rate',
            '_title': f'GDP Growth Rate — {self.continent} ({self.year_start}–{self.year_end})',
            'country':     country,
            'growth_rate': round(rate, 2),
            'year':        self.year_end
        }

        return list(filter(None, map(calc_growth, countries)))
    
    def _avg_by_continent(self, data: List[dict]) -> List[dict]:
        in_range = list(filter(
        lambda row: row.get(str(self.year_start)) is not None or
                    row.get(str(self.year_end)) is not None,
        data
        ))

        continents = list(set(map(
        lambda row: row.get('Continent'),
        in_range
        )))

        def continent_avg(continent):
            rows = list(filter(
            lambda r: r.get('Continent') == continent,
            in_range
        ))

            years = range(self.year_start, self.year_end + 1)

            all_gdp_values = list(filter(
                lambda v: v is not None,
                chain.from_iterable(map(
                lambda row: map(lambda yr: row.get(str(yr)), years),
                rows
                ))
            ))

            if not all_gdp_values:
                return None

            avg = sum(all_gdp_values) / len(all_gdp_values)

            return {
            '_chart_type': 'avg_gdp_by_continent',
            '_title': f'Average GDP by Continent ({self.year_start}–{self.year_end})',
            'continent': continent,
            'avg_gdp':   round(avg, 2)
            }

        return list(filter(None, map(continent_avg, continents)))
    
    def _global_trend(self, data: List[dict]) -> List[dict]:
        years = list(range(self.year_start, self.year_end + 1))

        def year_total(year):
            gdp_values = list(filter(
            lambda v: v is not None,
            map(lambda row: row.get(str(year)), data)
            ))

            if not gdp_values:
                return None

            total = sum(gdp_values)

            return {
            '_chart_type': 'global_gdp_trend',
            '_title': f'Total Global GDP Trend ({self.year_start}–{self.year_end})',
            'year':      year,
            'total_gdp': round(total, 2)
            }

        return list(filter(None, map(year_total, years)))
    
    def _fastest_growing(self, data: List[dict]) -> List[dict]:
        continents = list(set(map(
        lambda row: row.get('Continent'),
        data
        )))

        def continent_growth(continent):
            rows = list(filter(
            lambda r: r.get('Continent') == continent,
            data
            ))

            gdp_start = list(filter(
            lambda v: v is not None,
            map(lambda r: r.get(str(self.year_start)), rows)
            ))

            gdp_end = list(filter(
            lambda v: v is not None,
            map(lambda r: r.get(str(self.year_end)), rows)
            ))

            if not gdp_start or not gdp_end:
                return None

            total_start = sum(gdp_start)
            total_end   = sum(gdp_end)

            if total_start == 0:
                return None

            growth_pct = ((total_end - total_start) / total_start) * 100

            return {
            'continent':  continent,
            'growth_pct': round(growth_pct, 2),
            'is_fastest': False
            }

        results = list(filter(None, map(continent_growth, continents)))

        if not results:
            return []

        fastest = max(results, key=lambda x: x['growth_pct'])

        tagged = list(map(
        lambda r: {**r,
                   '_chart_type': 'fastest_continent',
                   '_title': f'Fastest Growing Continent ({self.year_start}–{self.year_end})',
                   'is_fastest': r['continent'] == fastest['continent']},
        results
        ))

        return tagged

    def _consistent_decline(self, data: List[dict]) -> List[dict]:
        countries = list(set(map(
        lambda row: row.get('Country Name'),
        data
        )))

        def check_decline(country):
            rows = list(filter(
            lambda r: r.get('Country Name') == country,
            data
        ))

            if not rows:
                return None

            years = list(range(self.year_end - self.decline_years + 1,
                           self.year_end + 1))

            gdp_sequence = list(filter(
            lambda pair: pair[1] is not None,
            map(lambda yr: (yr, rows[0].get(str(yr))), years)
            ))

            if len(gdp_sequence) < self.decline_years:
                return None

            gdp_values = list(map(lambda pair: pair[1], gdp_sequence))

            pairs = list(zip(gdp_values, gdp_values[1:]))

            all_declining = all(map(
            lambda pair: pair[1] < pair[0],
            pairs
            ))

            if not all_declining:
                return None

            first_gdp = gdp_values[0]
            last_gdp  = gdp_values[-1]
            decline_pct = ((last_gdp - first_gdp) / first_gdp) * 100

            return {
            '_chart_type': 'consistent_decline',
            '_title': f'Countries with Consistent GDP Decline (Last {self.decline_years} Years)',
            'country':       country,
            'continent':     rows[0].get('Continent'),
            'decline_pct':   round(decline_pct, 2),
            'decline_years': self.decline_years
            }

        return list(filter(None, map(check_decline, countries)))

    def _continent_contribution(self, data: List[dict]) -> List[dict]:
        years = list(range(self.year_start, self.year_end + 1))

        continents = list(set(map(
        lambda row: row.get('Continent'),
        data
        )))

        def contribution_for_year(year):
            year_gdp_values = list(filter(
            lambda v: v is not None,
            map(lambda row: row.get(str(year)), data)
            ))

            if not year_gdp_values:
                return None

            world_gdp = sum(year_gdp_values)

            if world_gdp == 0:
                return None

            def continent_share(continent):
                cont_rows = list(filter(
                lambda r: r.get('Continent') == continent,
                data
            ))

                cont_gdp_values = list(filter(
                lambda v: v is not None,
                map(lambda r: r.get(str(year)), cont_rows)
            ))

                if not cont_gdp_values:
                    return None

                cont_gdp  = sum(cont_gdp_values)
                share_pct = (cont_gdp / world_gdp) * 100

                return {
                '_chart_type': 'continent_contribution',
                '_title': f'Continent Contribution to Global GDP ({self.year_start}–{self.year_end})',
                'year':      year,
                'continent': continent,
                'share_pct': round(share_pct, 2)
                }

            return list(filter(None, map(continent_share, continents)))

        nested = list(filter(None, map(contribution_for_year, years)))
    
        return list(filter(None, chain.from_iterable(nested)))
        
    
    
    
