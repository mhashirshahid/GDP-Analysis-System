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


def load(path: Path) -> dict:
    pass


def validate(cfg: dict) -> dict:
    pass