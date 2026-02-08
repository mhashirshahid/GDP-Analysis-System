def filter_data(data, region=None, year=None, country=None):
    check_criteria = lambda row: (
        (region is None or row['Region'] == region) and
        (year is None or row['Year'] == year) and (country is None or 
        row['Country'] == country)
    )
    return list(filter(check_criteria, data))

def get_gdp_stats(data, operation):
    
    if not data:
        return 0.0
    gdp_values = list(map(lambda row: row['GDP'], data))

    if operation.lower().strip() == "sum":
        return sum(gdp_values)
    
    elif operation.lower().strip() == "average":
        return sum(gdp_values) / len(gdp_values)
    else:
        raise ValueError(f"Invalid operation: {operation}, use sum or average")
