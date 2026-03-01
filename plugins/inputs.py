from __future__ import annotations

import csv
import io
import json
import logging
import re
from functools import partial, reduce
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_RE_NAN     = re.compile(r'\bNaN\b')
_RE_GARBAGE = re.compile(r'#@\$!\\')

_META_KEYS = frozenset({"country name", "country code", "indicator name", "indicator code", "continent"})
_BAD_VALS  = frozenset({"", "nan", "none", "#@$!\\", "null", "n/a"})


def _coerce_value(value: Any) -> float | None:
    pass


def _normalize_record(raw: dict) -> dict:
    pass


def _validate_records(records: list[dict]) -> list[dict]:
    pass


def _patch_json(text: str) -> str:
    pass


def _parse_json(text: str) -> list[dict]:
    pass


def _parse_csv(text: str) -> list[dict]:
    pass


class JSONReader:
    def __init__(self, filepath: str, service: Any) -> None:
        pass

    def run(self) -> None:
        pass

    def _load(self) -> list[dict]:
        pass


class CSVReader:
    def __init__(self, filepath: str, service: Any) -> None:
        pass

    def run(self) -> None:
        pass

    def _load(self) -> list[dict]:
        pass