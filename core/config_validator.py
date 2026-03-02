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
]


def load(path: Path) -> dict:
    pass


def validate(cfg: dict) -> dict:
    pass