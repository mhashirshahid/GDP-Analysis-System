# GDP Analysis System

A configuration-driven GDP data analysis tool built with Python, featuring both interactive GUI and batch processing modes. This project implements functional programming principles and the Single Responsibility Principle (SRP) to analyze World Bank GDP data.

## Project Overview

This system provides two operational modes:

1. **GUI Mode**: Interactive dashboard with dropdown filters, real-time statistics, and multiple visualization types
2. **Script Mode**: Batch processing that generates and saves comprehensive analysis dashboards

## Project Structure

```
GDP-Analysis-System/
│
├── data/
│   └── gdp_data.csv              # World Bank GDP dataset
│
├── GUI/
│   ├── __init__.py
│   └── app.py                    # Tkinter-based GUI application
│
├── modules/
│   ├── __init__.py
│   ├── loader.py                 # CSV data loading with functional transforms
│   ├── processor.py              # Data filtering and statistical operations
│   └── visualizer.py             # Chart generation (matplotlib/seaborn)
│
├── outputs/                      # Generated visualization files
│
├── config.json                   # Configuration file (filters, paths, mode)
├── main.py                       # Entry point
└── README.md

```

## Features

### Data Processing
- CSV data loading with UTF-8 BOM handling
- Functional programming constructs (map, filter, lambda)
- Dynamic filtering by region, year, and country
- Statistical operations: sum, average

### Visualizations
- Bar Chart: Regional GDP comparison (adaptive horizontal/vertical layout)
- Pie Chart: Market share distribution
- Histogram: GDP wealth distribution with KDE overlay
- Line Chart: Historical GDP trends for selected economies

### GUI Features
- Real-time region and year filtering
- Dynamic statistics sidebar (Total GDP, Average GDP, Country Count)
- Four interactive visualization modes
- Error handling with user-friendly dialogs

## Requirements

### Dependencies

```
matplotlib>=3.5.0
seaborn>=0.12.0
```

### Python Version
- Python 3.7 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mhashirshahid/GDP-Analysis-System
cd GDP-Analysis-System
```

2. Install required packages:
```bash
pip install matplotlib seaborn
```

3. Ensure your dataset is placed in the `data/` directory as `gdp_data.csv`

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "app_mode": "gui",
  "data_file": "data/gdp_data.csv",
  "filters": {
    "region": "Asia",
    "year": 2018,
    "country": null
  },
  "operation": "sum",
  "plot": {
    "show_plot": true,
    "save_path": "outputs/dashboard.png"
  }
}
```

### Configuration Parameters

- **app_mode**: `"gui"` for interactive mode, any other value for script mode
- **data_file**: Path to the CSV dataset
- **filters.region**: Default region filter (e.g., "Asia", "Europe", "Africa")
- **filters.year**: Default year filter (e.g., 2018)
- **filters.country**: Specific country filter (optional, used in script mode)
- **operation**: Statistical operation (`"sum"` or `"average"`)
- **plot.show_plot**: Display plot window in script mode (true/false)
- **plot.save_path**: Output file path for generated visualizations

## Usage

### Running GUI Mode

```bash
python main.py
```

Ensure `config.json` has `"app_mode": "gui"`. The application will launch an interactive window where you can:

1. Select region and year from dropdown menus
2. View real-time statistics in the sidebar
3. Switch between visualization types using radio buttons
4. Explore regional comparisons, market share, wealth distribution, and historical trends

### Running Script Mode

Set `"app_mode"` to any value other than `"gui"` in `config.json`:

```json
{
  "app_mode": "script",
  ...
}
```

Then run:

```bash
python main.py
```

This will:
- Load data based on configuration
- Apply filters from `config.json`
- Generate a comprehensive dashboard with three charts
- Save output to the path specified in `plot.save_path`

## Dataset Format

The CSV file should contain the following columns:

- **Country Name**: Name of the country
- **Continent**: Region/continent classification
- **[Year columns]**: GDP values for specific years (e.g., "2010", "2011", etc.)

Example:
```csv
Country Name,Continent,2010,2011,2012,...
United States,North America,14964372000000,15517900000000,...
China,Asia,6087160000000,7551500000000,...
```

## Module Responsibilities

### loader.py
- Reads CSV files with proper encoding
- Transforms wide-format data into normalized records
- Validates year columns and GDP values
- Returns list of dictionaries: `[{'Country': str, 'Year': int, 'GDP': float, 'Region': str}, ...]`

### processor.py
- `filter_data()`: Filters dataset by region, year, or country using lambda functions
- `get_gdp_stats()`: Computes sum or average of GDP values

### visualizer.py
- `aggregate_data()`: Groups top N countries and aggregates remainder into "Other"
- `create_dashboard()`: Generates three-panel dashboard (script mode)
- `get_bar_figure()`: Creates bar chart with adaptive orientation
- `get_pie_figure()`: Creates market share pie chart
- `get_histogram_figure()`: Creates GDP distribution histogram with KDE
- `get_line_figure()`: Creates time-series line chart

### GUI/app.py
- `GDPApp`: Main Tkinter application class
- Manages sidebar controls and content area
- Dynamically refreshes visualizations based on user selections
- Displays real-time statistics

## Output Files

When running in script mode, the system generates:

- **outputs/dashboard.png**: High-resolution (300 DPI) dashboard containing:
  - Top 15 economies bar chart with "Other" category
  - Market share pie chart (Top 9 + Other)
  - GDP growth trend line for the largest economy in the selected region

Output directory is created automatically if it doesn't exist.

## Error Handling

The system handles:

- Missing or invalid CSV files (FileNotFoundError)
- Missing configuration file (exits with error message)
- Empty datasets after filtering (displays warnings)
- Invalid operations in `get_gdp_stats()` (ValueError)
- GUI data loading failures (error dialog boxes)

## Design Principles

### Single Responsibility Principle
- Each module handles one aspect: loading, processing, or visualization
- Clear separation between data layer and presentation layer

### Functional Programming
- Extensive use of `map()`, `filter()`, and `lambda` expressions
- Avoids traditional for-loops where possible
- Immutable data transformations

### Configuration-Driven
- No hardcoded region, year, or operation values
- All behavior controlled through `config.json`
- Easy to modify analysis parameters without code changes

## Troubleshooting

**Issue**: GUI window doesn't launch
- **Solution**: Verify `config.json` has `"app_mode": "gui"` and tkinter is installed

**Issue**: No output file generated
- **Solution**: Check `app_mode` is NOT "gui" and verify `plot.save_path` permissions

**Issue**: Empty visualizations
- **Solution**: Verify your CSV has data for the selected region/year combination

**Issue**: Import errors for modules
- **Solution**: Ensure you're running from the project root directory

## Development

This project was developed following academic requirements for:
- Functional programming paradigm
- Single Responsibility Principle (SRP)
- Configuration-driven architecture
- Version control with incremental Git commits

## License

This project is developed as part of an academic assignment (SDA Project Phase 1).

## Contributors

Project completed in pairs as per course requirements. Refer to Git commit history for individual contributions.