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
}

_CONFIG_PATH   = Path("config.json")
_VALID_YEARS   = range(1960, 2025)
_VALID_CONTS   = {"Africa", "Asia", "Europe", "North America",
                  "Oceania", "South America", "Global"}


def _yr(c):  return c.get("filters", {}).get("year_range", [None, None])
def _f(c):   return c.get("filters", {})
def _p(c):   return c.get("plot", {})


class ConfigError(Exception):
    pass


def _load_config(path: Path) -> dict:
    pass


def _validate_config(cfg: dict) -> dict:
    pass


def _build_sink(cfg: dict) -> Any:
    pass


def _build_engine(cfg: dict, sink: Any) -> Any:
    pass


def _build_reader(cfg: dict, engine: Any) -> Any:
    pass


def bootstrap() -> None:
    pass


def main() -> None:
    pass


if __name__ == "__main__":
    main()