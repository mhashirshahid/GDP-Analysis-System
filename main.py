from __future__ import annotations

import json
import logging
import os
import sys
from functools import reduce
from pathlib import Path
from typing import Any

from core.engine import TransformationEngine
from plugins.inputs  import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter
from plugins.outputs import ConsoleWriter, GraphicsChartWriter, GUISink

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger(__name__)

INPUT_DRIVERS: dict[str, type] = {
    "json": JSONReader,
    "csv":  CSVReader,
}

OUTPUT_DRIVERS: dict[str, type] = {
    "console": ConsoleWriter,
    "chart":   GraphicsChartWriter,
    "gui":     GUISink,
}

_CONFIG_PATH   = Path("config.json")
_VALID_YEARS   = range(1960, 2025)
_VALID_CONTS   = {"Africa", "Asia", "Europe", "North America",
                  "Oceania", "South America", "Global"}


def _yr(c):  return c.get("filters", {}).get("year_range", [None, None])
def _f(c):   return c.get("filters", {})
def _p(c):   return c.get("plot", {})


_RULES = [
    ("'input_driver' key is missing.",
     lambda c: "input_driver" in c),

    ("'output_driver' key is missing.",
     lambda c: "output_driver" in c),

    ("'data_file' key is missing.",
     lambda c: "data_file" in c),

    ("'filters' key is missing or is not an object {}.",
     lambda c: isinstance(c.get("filters"), dict)),

    (lambda c: f"'input_driver' must be a string, got {type(c.get('input_driver')).__name__}.",
     lambda c: isinstance(c.get("input_driver"), str)),

    (lambda c: f"'output_driver' must be a string, got {type(c.get('output_driver')).__name__}.",
     lambda c: isinstance(c.get("output_driver"), str)),

    (lambda c: f"'data_file' must be a non-empty string, got {type(c.get('data_file')).__name__}.",
     lambda c: isinstance(c.get("data_file"), str) and len(c.get("data_file", "").strip()) > 0),

    (lambda c: f"Unknown input_driver '{c.get('input_driver')}'. Valid options: {sorted(INPUT_DRIVERS)}.",
     lambda c: not isinstance(c.get("input_driver"), str) or c.get("input_driver") in INPUT_DRIVERS),

    (lambda c: f"Unknown output_driver '{c.get('output_driver')}'. Valid options: {sorted(OUTPUT_DRIVERS)}.",
     lambda c: not isinstance(c.get("output_driver"), str) or c.get("output_driver") in OUTPUT_DRIVERS),

    (lambda c: f"filters.continent must be a string, got {type(_f(c).get('continent')).__name__}.",
     lambda c: not isinstance(c.get("filters"), dict) or isinstance(_f(c).get("continent", ""), str)),

    (lambda c: f"filters.year must be an integer, got {type(_f(c).get('year')).__name__}.",
     lambda c: not isinstance(c.get("filters"), dict) or isinstance(_f(c).get("year", 0), int)),

    (lambda c: f"filters.year_range must be a list of exactly 2 integers, e.g. [2010, 2023].",
     lambda c: not isinstance(c.get("filters"), dict) or (
         isinstance(_f(c).get("year_range"), list) and
         len(_f(c).get("year_range", [])) == 2 and
         all(map(lambda v: isinstance(v, int), _f(c).get("year_range", [])))
     )),

    (lambda c: f"filters.decline_years must be a positive integer, got {_f(c).get('decline_years')}.",
     lambda c: not isinstance(c.get("filters"), dict) or (
         isinstance(_f(c).get("decline_years", 1), int) and _f(c).get("decline_years", 1) > 0
     )),

    (lambda c: f"filters.continent '{_f(c).get('continent')}' is not recognised. "
               f"Valid: {sorted(_VALID_CONTS)}.",
     lambda c: not isinstance(c.get("filters"), dict) or
               not isinstance(_f(c).get("continent"), str) or
               _f(c).get("continent") in _VALID_CONTS),

    (lambda c: f"filters.year {_f(c).get('year')} is out of range. Must be between 1960 and 2024.",
     lambda c: not isinstance(c.get("filters"), dict) or
               not isinstance(_f(c).get("year"), int) or
               _f(c).get("year") in _VALID_YEARS),

    (lambda c: f"filters.year_range start ({_yr(c)[0]}) must be less than end ({_yr(c)[1]}).",
     lambda c: not isinstance(c.get("filters"), dict) or
               not (isinstance(_f(c).get("year_range"), list) and len(_f(c).get("year_range", [])) == 2) or
               _yr(c)[0] < _yr(c)[1]),

    (lambda c: f"filters.year_range [{_yr(c)[0]}, {_yr(c)[1]}] is outside supported data range 1960–2024.",
     lambda c: not isinstance(c.get("filters"), dict) or
               not (isinstance(_f(c).get("year_range"), list) and len(_f(c).get("year_range", [])) == 2) or
               (_yr(c)[0] in _VALID_YEARS and _yr(c)[1] in _VALID_YEARS)),

    (lambda c: f"filters.year {_f(c).get('year')} is outside year_range {_yr(c)}.",
     lambda c: not isinstance(c.get("filters"), dict) or
               not (isinstance(_f(c).get("year"), int) and
                    isinstance(_f(c).get("year_range"), list) and
                    len(_f(c).get("year_range", [])) == 2) or
               _yr(c)[0] <= _f(c).get("year") <= _yr(c)[1]),

    (lambda c: f"filters.decline_years ({_f(c).get('decline_years')}) must not exceed year_range span "
               f"({_yr(c)[1]} - {_yr(c)[0]} = {_yr(c)[1] - _yr(c)[0] if isinstance(_f(c).get('year_range'), list) and len(_f(c).get('year_range',[])) == 2 else '?'}).",
     lambda c: not isinstance(c.get("filters"), dict) or
               not (isinstance(_f(c).get("decline_years"), int) and
                    isinstance(_f(c).get("year_range"), list) and
                    len(_f(c).get("year_range", [])) == 2) or
               _f(c).get("decline_years", 1) <= (_yr(c)[1] - _yr(c)[0])),

    ("'plot' must be an object {} if provided.",
     lambda c: "plot" not in c or isinstance(c.get("plot"), dict)),

    ("plot.show_plot must be true or false.",
     lambda c: "plot" not in c or not isinstance(c.get("plot"), dict) or
               isinstance(_p(c).get("show_plot", False), bool)),

    ("plot.save_path must be a string or null.",
     lambda c: "plot" not in c or not isinstance(c.get("plot"), dict) or
               _p(c).get("save_path") is None or isinstance(_p(c).get("save_path"), str)),

    (lambda c: f"plot.save_path has an invalid file extension '{Path(str(_p(c).get('save_path',''))).suffix}'. "
               f"Use .png, .jpg, or .pdf.",
     lambda c: "plot" not in c or not isinstance(c.get("plot"), dict) or
               not isinstance(_p(c).get("save_path"), str) or
               Path(_p(c).get("save_path", "out.png")).suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf"}),

    (lambda c: f"Data file not found: '{c.get('data_file')}'. Check the path is relative to the project root.",
     lambda c: not isinstance(c.get("data_file"), str) or Path(c.get("data_file", "")).exists()),

    (lambda c: f"No read permission for data file: '{c.get('data_file')}'.",
     lambda c: not isinstance(c.get("data_file"), str) or
               not Path(c.get("data_file", "")).exists() or
               os.access(c.get("data_file"), os.R_OK)),

    (lambda c: f"Driver/file mismatch: input_driver is '{c.get('input_driver')}' but "
               f"data_file '{c.get('data_file')}' has extension "
               f"'{Path(str(c.get('data_file',''))).suffix}'. "
               f"Expected a .{c.get('input_driver','')} file (e.g. data/gdp_data.{c.get('input_driver','')}).",
     lambda c: not isinstance(c.get("input_driver"), str) or
               not isinstance(c.get("data_file"), str) or
               c.get("input_driver") not in INPUT_DRIVERS or
               Path(c.get("data_file", "x.x")).suffix.lstrip(".").lower() == c.get("input_driver", "")),
]


class ConfigError(Exception):
    pass


def _load_config(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(
            f"config.json not found at: {path.resolve()}\n"
            f"  Make sure you are running from the project root directory."
        )
    if not os.access(path, os.R_OK):
        raise ConfigError(f"No read permission for config.json at: {path.resolve()}")
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ConfigError("config.json is empty.")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"config.json contains invalid JSON.\n"
            f"  Line {exc.lineno}, column {exc.colno}: {exc.msg}\n"
            f"  Tip: use a JSON validator (e.g. jsonlint.com) to find the exact error."
        ) from exc
    if not isinstance(result, dict):
        raise ConfigError(
            f"config.json must be a JSON object {{}} at the top level, "
            f"got {type(result).__name__}."
        )
    return result


def _validate_config(cfg: dict) -> dict:
    def _check(rule):
        msg_or_fn, pred = rule
        try:
            passed = pred(cfg)
        except Exception:
            passed = False
        return None if passed else (msg_or_fn(cfg) if callable(msg_or_fn) else msg_or_fn)

    failures = list(filter(None, map(_check, _RULES)))
    if failures:
        detail = reduce(lambda acc, m: acc + f"\n  ✗  {m}", failures, "")
        raise ConfigError(f"config.json validation failed:{detail}")
    return cfg

def _build_sink(cfg: dict) -> Any:
    key = cfg["output_driver"]
    cls = OUTPUT_DRIVERS[key]
    plot = cfg.get("plot", {})
    kwargs = {
        "chart":   {"show_plot": plot.get("show_plot", False),
                    "save_path": plot.get("save_path", None)},
        "console": {},
        "gui":     {},
    }.get(key, {})
    return cls(**kwargs)

def _build_engine(cfg: dict, sink: Any) -> Any:
    engine = TransformationEngine(sink=sink, config=cfg)
    log.info("Engine: %s", type(engine).__name__)
    return engine


def _build_reader(cfg: dict, engine: Any) -> Any:
    reader = INPUT_DRIVERS[cfg["input_driver"]](filepath=cfg["data_file"], service=engine)
    log.info("Reader: %s", type(reader).__name__)
    return reader


def bootstrap() -> None:
    log.info("━━━  GDP Analysis System — Phase 2  ━━━")

    def _load(_):      return _load_config(_CONFIG_PATH)
    def _validate(cfg): return _validate_config(cfg)
    def _wire(cfg):
        sink   = _build_sink(cfg)
        engine = _build_engine(cfg, sink)
        reader = _build_reader(cfg, engine)
        return {**cfg, "_sink": sink, "_engine": engine, "_reader": reader}
    def _run(ctx):
        ctx["_reader"].run()
        if isinstance(ctx["_sink"], GUISink):
            ctx["_sink"].launch()
        return ctx

    reduce(lambda acc, fn: fn(acc), [_load, _validate, _wire, _run], None)
    log.info("━━━  Done  ━━━")


def main() -> None:
    debug = "--debug" in sys.argv
    try:
        bootstrap()
    except ConfigError as exc:
        print(f"\n[CONFIG ERROR]\n{exc}\n", file=sys.stderr)
        if debug: raise
        sys.exit(1)
    except RuntimeError as exc:
        print(f"\n[RUNTIME ERROR]\n{exc}\n", file=sys.stderr)
        if debug: raise
        sys.exit(2)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"\n[UNEXPECTED ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
        print("Run with --debug for full traceback.", file=sys.stderr)
        if debug: raise
        sys.exit(3)


if __name__ == "__main__":
    main()