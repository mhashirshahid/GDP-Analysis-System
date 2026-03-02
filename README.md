# GDP Analysis System — Phase 2

A configuration-driven, modular GDP data analysis tool built with Python. Phase 2 refactors the original script into a **fully decoupled architecture** using the Dependency Inversion Principle (DIP), structural typing via `Protocol`, and Dependency Injection — while maintaining strict functional programming throughout.

## Project Overview

The system reads World Bank GDP data (CSV or JSON), runs eight analytical computations, and outputs results to the terminal, as saved chart images, or through an interactive GUI dashboard — all controlled entirely through `config.json` without touching any source code.

## Project Structure

```
GDP-Analysis-System/
│
├── core/
│   ├── __init__.py
│   ├── contracts.py          # DataSink and PipelineService Protocols
│   ├── config_validator.py   # Config loading, validation rules, ConfigError
│   └── engine.py             # TransformationEngine — all 8 analytical outputs
│
├── data/
│   ├── gdp_with_continent_filled.csv
│   └── gdp_with_continent_filled.json
│
├── docs/
│   ├── architecture.png      # Module dependency diagram
│   └── diagram.puml          # PlantUML source
│
├── GUI/
│   └── dashboard.py          # Tkinter GUI dashboard with sidebar navigation
│
├── outputs/                  # Generated chart images (auto-created on run)
│   ├── dashboard_top_10_gdp.png
│   ├── dashboard_bottom_10_gdp.png
│   ├── dashboard_gdp_growth_rate.png
│   ├── dashboard_avg_gdp_by_continent.png
│   ├── dashboard_global_gdp_trend.png
│   ├── dashboard_fastest_continent.png
│   ├── dashboard_consistent_decline.png
│   └── dashboard_continent_contribution.png
│
├── plugins/
│   ├── __init__.py
│   ├── inputs.py             # CSVReader, JSONReader
│   └── outputs.py            # ConsoleWriter, GraphicsChartWriter, GUISink
│
├── config.json               # Runtime configuration
├── main.py                   # Orchestrator / Bootstrap
└── README.md
```

## Architecture

Phase 2 is built around the **Dependency Inversion Principle**. The Core never imports from plugins — it owns the contracts, and plugins conform to them.

```
plugins/inputs.py  ──►  PipelineService (core/contracts.py)  ◄──  core/engine.py
plugins/outputs.py ──►  DataSink        (core/contracts.py)  ◄──  core/engine.py
                                ▲
                           main.py
                     (wires everything together)
```

Data flow at runtime:

```
config.json  →  main.py  →  Reader.run()  →  Engine.execute()  →  Writer.write()
```

`main.py` is the only place that knows which concrete classes are in use. Swapping a reader or writer is a one-line change in `config.json`.

## Analytical Outputs

The engine produces eight outputs on every run:

| # | Output | Config Keys Used |
|---|--------|-----------------|
| 1 | Top 10 Countries by GDP | `continent`, `year` |
| 2 | Bottom 10 Countries by GDP | `continent`, `year` |
| 3 | GDP Growth Rate per Country | `continent`, `year_range` |
| 4 | Average GDP by Continent | `year_range` |
| 5 | Total Global GDP Trend | `year_range` |
| 6 | Fastest Growing Continent | `year_range` |
| 7 | Countries with Consistent GDP Decline | `year_range`, `decline_years` |
| 8 | Continent Contribution to Global GDP | `year_range` |

## Requirements

### Dependencies

```
matplotlib>=3.5.0
openpyxl>=3.0.0
```

### Python Version
- Python 3.10 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mhashirshahid/GDP-Analysis-System
cd GDP-Analysis-System
```

2. Checkout the Phase 2 branch:
```bash
git checkout phase-2
```

3. Install dependencies:
```bash
pip install matplotlib openpyxl
```

4. Ensure your dataset is in the `data/` directory.

## Configuration

All runtime behaviour is controlled through `config.json`. No source code changes are needed to switch inputs, outputs, or filters.

```json
{
  "input_driver": "json",
  "output_driver": "gui",

  "data_file": "data/gdp_with_continent_filled.json",

  "filters": {
    "continent": "Asia",
    "year": 2019,
    "year_range": [2010, 2023],
    "decline_years": 5
  },

  "plot": {
    "show_plot": false,
    "save_path": "outputs/dashboard.png"
  }
}
```

### Configuration Parameters

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `input_driver` | `"csv"` \| `"json"` | ✅ | Which reader to use |
| `output_driver` | `"console"` \| `"chart"` \| `"gui"` | ✅ | Which writer to use |
| `data_file` | string | ✅ | Path to dataset, relative to project root |
| `filters.continent` | string | ✅ | Continent to analyse (e.g. `"Asia"`, `"Europe"`) |
| `filters.year` | integer | ✅ | Single year for Top/Bottom 10 (e.g. `2019`) |
| `filters.year_range` | `[start, end]` | ✅ | Date range for trend analyses |
| `filters.decline_years` | integer | ✅ | Consecutive years of decline to flag |
| `plot.show_plot` | boolean | only for `chart` | Display chart window interactively |
| `plot.save_path` | string | only for `chart` | File path for saved charts (`.png`, `.jpg`, `.pdf`) |

### Valid Values

- **continent**: `Africa`, `Asia`, `Europe`, `North America`, `Oceania`, `South America`, `Global`
- **year / year_range**: Any value between `1960` and `2024`
- `year` must fall within `year_range`
- `decline_years` must be a positive integer and cannot exceed the `year_range` span

## Usage

### Interactive GUI dashboard

```json
"output_driver": "gui"
```

```bash
python main.py
```

Opens a full-screen dashboard with a sidebar listing all 8 charts. Click any item in the sidebar or use keyboard shortcuts to navigate.

**Keyboard shortcuts:**
- `←` / `→` — previous / next chart
- `1` – `8` — jump directly to a chart
- `Esc` — close

### Print results to terminal

```json
"output_driver": "console"
```

```bash
python main.py
```

### Save charts to disk

```json
"output_driver": "chart",
"plot": {
  "show_plot": false,
  "save_path": "outputs/dashboard.png"
}
```

```bash
python main.py
```

Each of the 8 outputs is saved as a separate file, automatically suffixed:

```
outputs/dashboard_top_10_gdp.png
outputs/dashboard_bottom_10_gdp.png
outputs/dashboard_gdp_growth_rate.png
outputs/dashboard_avg_gdp_by_continent.png
outputs/dashboard_global_gdp_trend.png
outputs/dashboard_fastest_continent.png
outputs/dashboard_consistent_decline.png
outputs/dashboard_continent_contribution.png
```

### Debugging

```bash
python main.py --debug
```

Shows the full traceback instead of the clean error message.

### Switching data source

```json
"input_driver": "json",
"data_file": "data/gdp_with_continent_filled.json"
```

No other changes needed.

## Chart Personalities

Each chart has its own distinct visual theme:

| Chart | Theme | Signature |
|-------|-------|-----------|
| 🏆 Top 10 by GDP | Hall of Fame | Gold-to-bronze gradient bars, warm amber background |
| 🧊 Bottom 10 by GDP | The Cellar | Ice-blue gradient fading to deep navy |
| 🏎 GDP Growth Rate | The Race | Vivid green/red diverging bars with bold zero-line |
| 🌍 Average GDP by Continent | Around the World | Each continent rendered in its own geographic colour |
| 🌌 Global GDP Trend | Cosmic | Deep space background with triple-layered neon cyan glow |
| 🔥 Fastest Growing Continent | Champion's Podium | Winner blazes orange-red, all others charcoal |
| ⚠ Consistent Decline | Red Alert | Blood-red intensity gradient with full warning border |
| 🎼 Continent Share | Symphony | Festival-palette stacked area on deep midnight background |

## Module Responsibilities

### `core/contracts.py`
Defines the two structural interfaces (Protocols) that govern all data flow:
- `DataSink`: requires `write(records: List[dict]) -> None` — implemented by output plugins
- `PipelineService`: requires `execute(raw_data: List[Any]) -> None` — implemented by the engine

### `core/config_validator.py`
Owns all configuration concerns so `main.py` stays clean:
- `ConfigError` — the single exception type raised for any config problem
- `load(path)` — reads and parses `config.json`, catching filesystem and JSON errors before any rule runs
- `validate(cfg)` — runs 30+ rules covering required keys, types, value ranges, cross-field consistency, filesystem access, and driver/extension agreement. All failures are collected and reported together in one message.

### `core/engine.py`
The `TransformationEngine` class. Receives a `DataSink` at construction (injected by `main.py`) and a config dict. On `execute()`, runs all 8 analytical computations using `map`, `filter`, and `functools.reduce`, then calls `sink.write()` once per output.

### `plugins/inputs.py`
- `JSONReader`: patches non-standard tokens (`NaN`, `#@$!\`) before parsing, then normalises and validates records
- `CSVReader`: reads UTF-8 CSV with BOM handling, normalises year keys to strings and GDP values to `float | None`

Both push cleaned records into the injected service via `service.execute()`.

### `plugins/outputs.py`
- `ConsoleWriter`: prints each result batch to the terminal in a clean columnar layout, dispatched by `_chart_type`
- `GraphicsChartWriter`: renders each result batch as a themed matplotlib chart and saves to disk; top 10 and bottom 10 are saved as separate files
- `GUISink`: collects all rendered figures in memory, then hands them to `GUIDashboard` via `launch()`

### `GUI/dashboard.py`
`GUIDashboard` — a `tk.Tk` subclass that displays all 8 charts in a navigable window. Features a persistent sidebar with numbered chart entries, active-state highlighting, hover effects, keyboard navigation, and direct jump-to-chart via number keys.

### `main.py`
The orchestrator. Imports `load` and `validate` from `core/config_validator`, wires all components together via Dependency Injection, and handles process exit codes for every error category. A `_show_error_window()` helper surfaces `ConfigError` and `RuntimeError` in a native OS dialog in addition to stderr, so errors are visible even when launching without a terminal.

```
Sink → Engine(sink) → Reader(engine) → reader.run()
```

Factory dictionaries map driver name strings to concrete classes — adding a new driver requires one line here and nothing else.

## Config Validation

`core/config_validator.py` validates every field before any component is instantiated. All failures are collected and reported together:

```
[CONFIG ERROR]
config.json validation failed:
  ✗  filters.continent is required.
  ✗  filters.year 2000 is outside year_range [2010, 2023].
  ✗  filters.decline_years (99) cannot exceed year_range span (13).
```

Every validated case:

| Category | What is checked |
|----------|----------------|
| Missing keys | All four top-level keys + all four `filters` sub-keys are required |
| Wrong types | Strings, plain integers (booleans rejected), lists of integers, booleans |
| Null values | Any required field set to `null` is caught |
| Empty strings | `""` and whitespace-only strings rejected for `continent` and `data_file` |
| Unknown drivers | `input_driver` and `output_driver` checked against known values |
| Invalid continent | Checked against the seven valid continent names |
| Year out of range | `year` and both `year_range` values must be 1960–2024 |
| Year range order | `year_range[0]` must be strictly less than `year_range[1]` |
| Year outside range | `year` must fall within `year_range` |
| Decline years span | `decline_years` cannot exceed the `year_range` span |
| Plot block | `show_plot` must be boolean; `save_path` must be a valid non-empty string or null |
| Save path extension | Only `.png`, `.jpg`, `.jpeg`, `.pdf` are accepted |
| Chart requires plot | `output_driver: "chart"` without a `plot` block is caught |
| File not found | `data_file` path is verified to exist and be a file, not a directory |
| File permissions | Read access on `data_file` is verified |
| Driver/extension match | `input_driver` must match the file extension of `data_file` |

## Design Principles

### Dependency Inversion Principle (DIP)
High-level modules (Core) do not depend on low-level modules (plugins). Both depend on abstractions (`Protocol`). The Core owns and defines the contracts; plugins conform to them.

### Dependency Injection
`main.py` constructs all concrete objects and passes them inward. The engine never instantiates a writer; the reader never instantiates an engine. Each component receives its dependencies through its constructor.

### Functional Programming
No `for` or `while` loops anywhere in the codebase — including list/dict comprehensions and generator expressions. All iteration is expressed through `map()`, `filter()`, `functools.reduce()`, and `itertools`.

### Configuration-Driven
Zero hardcoded filters, paths, or driver names outside `config.json`. Changing the continent, year range, input format, or output format requires only editing the config file.

### Separation of Concerns
Config validation lives entirely in `core/config_validator.py`. Chart rendering themes live entirely in `plugins/outputs.py`. GUI layout lives entirely in `GUI/dashboard.py`. `main.py` contains only orchestration.

## Troubleshooting

**Issue**: `[CONFIG ERROR] Driver/file mismatch`
- **Solution**: Make sure `input_driver` and the extension of `data_file` match — `"csv"` with a `.csv` file, `"json"` with a `.json` file.

**Issue**: `[CONFIG ERROR] filters.continent is required`
- **Solution**: All four `filters` sub-keys (`continent`, `year`, `year_range`, `decline_years`) are mandatory.

**Issue**: Empty chart or `No data` message
- **Solution**: The selected `continent` or `year` has no data in the dataset. Try `"Asia"` with `year: 2019`.

**Issue**: `ModuleNotFoundError: No module named 'core'`
- **Solution**: Run from the project root directory, not from inside a subfolder.

**Issue**: `ModuleNotFoundError: No module named 'matplotlib'`
- **Solution**: Run `pip install matplotlib`.