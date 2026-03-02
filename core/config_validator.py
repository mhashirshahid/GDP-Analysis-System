from __future__ import annotations

import json
import os
from functools import reduce
from pathlib import Path


class ConfigError(Exception):
    pass


_VALID_YEARS  = range(1960, 2025)
_VALID_CONTS  = {"Africa", "Asia", "Europe", "North America",
                 "Oceania", "South America", "Global"}
_VALID_EXTS   = {".png", ".jpg", ".jpeg", ".pdf"}
_INPUT_EXTS   = {"csv", "json"}
_OUTPUT_MODES = {"console", "chart", "gui"}


def _yr(c): return c.get("filters", {}).get("year_range", [None, None])
def _f(c):  return c.get("filters", {})
def _p(c):  return c.get("plot", {})


_RULES: list[tuple] = [

    # Required top-level keys
    ("'input_driver' is missing.",
     lambda c: "input_driver" in c),

    ("'output_driver' is missing.",
     lambda c: "output_driver" in c),

    ("'data_file' is missing.",
     lambda c: "data_file" in c),

    ("'filters' is missing or is not an object {}.",
     lambda c: isinstance(c.get("filters"), dict)),

    # Type checks
    (lambda c: f"'input_driver' must be a string, got {type(c.get('input_driver')).__name__}.",
     lambda c: isinstance(c.get("input_driver"), str)),

    (lambda c: f"'output_driver' must be a string, got {type(c.get('output_driver')).__name__}.",
     lambda c: isinstance(c.get("output_driver"), str)),

    (lambda c: f"'data_file' must be a non-empty string, got {type(c.get('data_file')).__name__}.",
     lambda c: isinstance(c.get("data_file"), str) and bool(c.get("data_file", "").strip())),

    # Driver validity
    (lambda c: f"Unknown input_driver '{c.get('input_driver')}'. Valid: {sorted(_INPUT_EXTS)}.",
     lambda c: not isinstance(c.get("input_driver"), str)
               or c.get("input_driver") in _INPUT_EXTS),

    (lambda c: f"Unknown output_driver '{c.get('output_driver')}'. Valid: {sorted(_OUTPUT_MODES)}.",
     lambda c: not isinstance(c.get("output_driver"), str)
               or c.get("output_driver") in _OUTPUT_MODES),

    # filters field types
    (lambda c: f"filters.continent must be a string, got {type(_f(c).get('continent')).__name__}.",
     lambda c: not isinstance(c.get("filters"), dict)
               or isinstance(_f(c).get("continent", ""), str)),

    (lambda c: f"filters.year must be an integer, got {type(_f(c).get('year')).__name__}.",
     lambda c: not isinstance(c.get("filters"), dict)
               or isinstance(_f(c).get("year", 0), int)),

    ("filters.year_range must be a list of exactly 2 integers, e.g. [2010, 2023].",
     lambda c: not isinstance(c.get("filters"), dict) or (
         isinstance(_f(c).get("year_range"), list)
         and len(_f(c).get("year_range", [])) == 2
         and all(isinstance(v, int) for v in _f(c).get("year_range", []))
     )),

    (lambda c: f"filters.decline_years must be a positive integer, got {_f(c).get('decline_years')}.",
     lambda c: not isinstance(c.get("filters"), dict) or (
         isinstance(_f(c).get("decline_years", 1), int)
         and _f(c).get("decline_years", 1) > 0
     )),

    # filters value ranges
    (lambda c: f"filters.continent '{_f(c).get('continent')}' is not recognised. "
               f"Valid: {sorted(_VALID_CONTS)}.",
     lambda c: not isinstance(c.get("filters"), dict)
               or not isinstance(_f(c).get("continent"), str)
               or _f(c).get("continent") in _VALID_CONTS),

    (lambda c: f"filters.year {_f(c).get('year')} is out of range. Must be 1960–2024.",
     lambda c: not isinstance(c.get("filters"), dict)
               or not isinstance(_f(c).get("year"), int)
               or _f(c).get("year") in _VALID_YEARS),

    (lambda c: f"filters.year_range start ({_yr(c)[0]}) must be less than end ({_yr(c)[1]}).",
     lambda c: not isinstance(c.get("filters"), dict)
               or not (isinstance(_f(c).get("year_range"), list)
                       and len(_f(c).get("year_range", [])) == 2)
               or _yr(c)[0] < _yr(c)[1]),

    (lambda c: f"filters.year_range [{_yr(c)[0]}, {_yr(c)[1]}] is outside supported range 1960–2024.",
     lambda c: not isinstance(c.get("filters"), dict)
               or not (isinstance(_f(c).get("year_range"), list)
                       and len(_f(c).get("year_range", [])) == 2)
               or (_yr(c)[0] in _VALID_YEARS and _yr(c)[1] in _VALID_YEARS)),

    (lambda c: f"filters.year {_f(c).get('year')} is outside year_range {_yr(c)}.",
     lambda c: not isinstance(c.get("filters"), dict)
               or not (isinstance(_f(c).get("year"), int)
                       and isinstance(_f(c).get("year_range"), list)
                       and len(_f(c).get("year_range", [])) == 2)
               or _yr(c)[0] <= _f(c).get("year") <= _yr(c)[1]),

    (lambda c: f"filters.decline_years ({_f(c).get('decline_years')}) cannot exceed "
               f"year_range span ({_yr(c)[1]} - {_yr(c)[0]} = "
               f"{_yr(c)[1] - _yr(c)[0] if isinstance(_f(c).get('year_range'), list) and len(_f(c).get('year_range', [])) == 2 else '?'}).",
     lambda c: not isinstance(c.get("filters"), dict)
               or not (isinstance(_f(c).get("decline_years"), int)
                       and isinstance(_f(c).get("year_range"), list)
                       and len(_f(c).get("year_range", [])) == 2)
               or _f(c).get("decline_years", 1) <= (_yr(c)[1] - _yr(c)[0])),

    # plot block
    ("'plot' must be an object {} if provided.",
     lambda c: "plot" not in c or isinstance(c.get("plot"), dict)),

    ("plot.show_plot must be true or false.",
     lambda c: "plot" not in c
               or not isinstance(c.get("plot"), dict)
               or isinstance(_p(c).get("show_plot", False), bool)),

    ("plot.save_path must be a non-empty string or null.",
     lambda c: "plot" not in c
               or not isinstance(c.get("plot"), dict)
               or _p(c).get("save_path") is None
               or (isinstance(_p(c).get("save_path"), str)
                   and bool(_p(c).get("save_path", "").strip()))),

    (lambda c: f"plot.save_path has an invalid extension "
               f"'{Path(str(_p(c).get('save_path', ''))).suffix}'. Use: .png .jpg .pdf.",
     lambda c: "plot" not in c
               or not isinstance(c.get("plot"), dict)
               or not isinstance(_p(c).get("save_path"), str)
               or Path(_p(c).get("save_path", "out.png")).suffix.lower() in _VALID_EXTS),

    # chart driver requires a plot block
    ("output_driver 'chart' requires a 'plot' block with a valid save_path.",
     lambda c: c.get("output_driver") != "chart"
               or (isinstance(c.get("plot"), dict)
                   and isinstance(_p(c).get("save_path"), str)
                   and bool(_p(c).get("save_path", "").strip()))),

    # filesystem
    (lambda c: f"Data file not found: '{c.get('data_file')}'. "
               f"Path is relative to the project root.",
     lambda c: not isinstance(c.get("data_file"), str)
               or Path(c.get("data_file", "")).exists()),

    (lambda c: f"'{c.get('data_file')}' is a directory, not a file.",
     lambda c: not isinstance(c.get("data_file"), str)
               or not Path(c.get("data_file", "")).exists()
               or Path(c.get("data_file", "")).is_file()),

    (lambda c: f"No read permission for: '{c.get('data_file')}'.",
     lambda c: not isinstance(c.get("data_file"), str)
               or not Path(c.get("data_file", "")).is_file()
               or os.access(c.get("data_file"), os.R_OK)),

    # driver / file-extension agreement
    (lambda c: f"Driver/file mismatch: input_driver is '{c.get('input_driver')}' but "
               f"'{c.get('data_file')}' has extension "
               f"'{Path(str(c.get('data_file', ''))).suffix}'. "
               f"Expected a .{c.get('input_driver', '')} file.",
     lambda c: not isinstance(c.get("input_driver"), str)
               or not isinstance(c.get("data_file"), str)
               or c.get("input_driver") not in _INPUT_EXTS
               or Path(c.get("data_file", "x.x")).suffix.lstrip(".").lower()
               == c.get("input_driver", "")),
]


def load(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(
            f"config.json not found at: {path.resolve()}\n"
            f"  Make sure you are running from the project root directory."
        )
    if path.is_dir():
        raise ConfigError(f"Expected a file but found a directory at: {path.resolve()}")
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
            f"  Tip: validate at jsonlint.com."
        ) from exc

    if not isinstance(result, dict):
        raise ConfigError(
            f"config.json must be a JSON object {{}} at the top level, "
            f"got {type(result).__name__}."
        )
    return result


def validate(cfg: dict) -> dict:
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