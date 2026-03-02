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

def _has_f(c, k):   return isinstance(c.get("filters"), dict) and k in _f(c)
def _is_int(v):     return isinstance(v, int) and not isinstance(v, bool)
def _is_yr_list(v): return (
    isinstance(v, list)
    and len(v) == 2
    and all(_is_int(x) for x in v)
)


_RULES: list[tuple] = [

    # Required top-level keys
    ("'input_driver' is required.",
     lambda c: "input_driver" in c),

    ("'output_driver' is required.",
     lambda c: "output_driver" in c),

    ("'data_file' is required.",
     lambda c: "data_file" in c),

    ("'filters' is required and must be an object {}.",
     lambda c: isinstance(c.get("filters"), dict)),

    # Required filter sub-keys
    ("filters.continent is required.",
     lambda c: not isinstance(c.get("filters"), dict)
                or "continent" in _f(c)),

    ("filters.year is required.",
     lambda c: not isinstance(c.get("filters"), dict)
                or "year" in _f(c)),

    ("filters.year_range is required.",
     lambda c: not isinstance(c.get("filters"), dict)
                or "year_range" in _f(c)),

    ("filters.decline_years is required.",
     lambda c: not isinstance(c.get("filters"), dict)
                or "decline_years" in _f(c)),

    # Top-level type checks
    (lambda c: f"'input_driver' must be a string, got {type(c.get('input_driver')).__name__}.",
     lambda c: isinstance(c.get("input_driver"), str)),

    (lambda c: f"'output_driver' must be a string, got {type(c.get('output_driver')).__name__}.",
     lambda c: isinstance(c.get("output_driver"), str)),

    (lambda c: f"'data_file' must be a non-empty string, got {type(c.get('data_file')).__name__}.",
     lambda c: isinstance(c.get("data_file"), str)
                and bool(c.get("data_file", "").strip())),

    # Driver validity
    (lambda c: f"Unknown input_driver '{c.get('input_driver')}'. Valid: {sorted(_INPUT_EXTS)}.",
     lambda c: not isinstance(c.get("input_driver"), str)
                or c.get("input_driver") in _INPUT_EXTS),

    (lambda c: f"Unknown output_driver '{c.get('output_driver')}'. Valid: {sorted(_OUTPUT_MODES)}.",
     lambda c: not isinstance(c.get("output_driver"), str)
                or c.get("output_driver") in _OUTPUT_MODES),

    # Filter type checks
    (lambda c: f"filters.continent must be a non-empty string, "
                f"got {type(_f(c).get('continent')).__name__}.",
     lambda c: not _has_f(c, "continent")
                or (isinstance(_f(c).get("continent"), str)
                    and bool(_f(c).get("continent", "").strip()))),

    (lambda c: f"filters.year must be an integer, "
                f"got {type(_f(c).get('year')).__name__}"
                f"{' (booleans are not valid years)' if isinstance(_f(c).get('year'), bool) else ''}.",
     lambda c: not _has_f(c, "year")
                or _is_int(_f(c).get("year"))),

    (lambda c: f"filters.year_range must be a list of exactly 2 plain integers, "
                f"e.g. [2010, 2023]. Got: {_f(c).get('year_range')!r}.",
     lambda c: not _has_f(c, "year_range")
                or _is_yr_list(_f(c).get("year_range"))),

    (lambda c: f"filters.decline_years must be a positive integer, "
                f"got {_f(c).get('decline_years')!r}"
                f"{' (booleans are not valid)' if isinstance(_f(c).get('decline_years'), bool) else ''}.",
     lambda c: not _has_f(c, "decline_years")
                or (_is_int(_f(c).get("decline_years"))
                    and _f(c).get("decline_years") > 0)),

    # Filter value checks
    (lambda c: f"filters.continent '{_f(c).get('continent')}' is not recognised. "
                f"Valid: {sorted(_VALID_CONTS)}.",
     lambda c: not _has_f(c, "continent")
                or not isinstance(_f(c).get("continent"), str)
                or _f(c).get("continent") in _VALID_CONTS),

    (lambda c: f"filters.year {_f(c).get('year')} is out of range. Must be 1960–2024.",
     lambda c: not _has_f(c, "year")
                or not _is_int(_f(c).get("year"))
                or _f(c).get("year") in _VALID_YEARS),

    (lambda c: f"filters.year_range start ({_yr(c)[0]}) must be less than end ({_yr(c)[1]}).",
     lambda c: not _has_f(c, "year_range")
                or not _is_yr_list(_f(c).get("year_range"))
                or _yr(c)[0] < _yr(c)[1]),

    (lambda c: f"filters.year_range [{_yr(c)[0]}, {_yr(c)[1]}] is outside supported range 1960–2024.",
     lambda c: not _has_f(c, "year_range")
                or not _is_yr_list(_f(c).get("year_range"))
                or (_yr(c)[0] in _VALID_YEARS and _yr(c)[1] in _VALID_YEARS)),

    (lambda c: f"filters.year {_f(c).get('year')} is outside year_range {_yr(c)}.",
     lambda c: not _has_f(c, "year") or not _has_f(c, "year_range")
                or not _is_int(_f(c).get("year"))
                or not _is_yr_list(_f(c).get("year_range"))
                or _yr(c)[0] <= _f(c).get("year") <= _yr(c)[1]),

    (lambda c: f"filters.decline_years ({_f(c).get('decline_years')}) cannot exceed "
                f"year_range span "
                f"({_yr(c)[1]} - {_yr(c)[0]} = "
                f"{_yr(c)[1] - _yr(c)[0] if _is_yr_list(_f(c).get('year_range')) else '?'}).",
     lambda c: not _has_f(c, "decline_years") or not _has_f(c, "year_range")
                or not _is_int(_f(c).get("decline_years"))
                or not _is_yr_list(_f(c).get("year_range"))
                or _f(c).get("decline_years") <= (_yr(c)[1] - _yr(c)[0])),

    # plot block
    ("'plot' must be an object {} if provided.",
     lambda c: "plot" not in c
                or isinstance(c.get("plot"), dict)),

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
                f"'{Path(str(_p(c).get('save_path', ''))).suffix}'. "
                f"Use: .png .jpg .pdf.",
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

    # Filesystem
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

    # Driver / file-extension agreement
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