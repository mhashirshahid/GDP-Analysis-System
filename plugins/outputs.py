from __future__ import annotations

import logging
from functools import partial, reduce
from itertools import chain
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure

log = logging.getLogger(__name__)

_P = {
    "bg":       "#0d1117",
    "surface":  "#161b22",
    "border":   "#30363d",
    "text":     "#e6edf3",
    "subtext":  "#8b949e",
    "accent":   "#58a6ff",
    "positive": "#3fb950",
    "negative": "#f85149",
    "warning":  "#d29922",
    "hi":       "#bc8cff",
}

_COLORS = ["#58a6ff","#3fb950","#f85149","#d29922","#bc8cff","#79c0ff","#56d364"]

_SEP = "─" * 72


def _apply_theme(fig: Figure) -> Figure:
    pass


def _meta(records: list[dict], key: str, default: Any = None) -> Any:
    pass


def _strip(records: list[dict]) -> list[dict]:
    pass


def _fmt_gdp(v: float) -> str:
    pass


def _bar_color(v: float) -> str:
    pass


def _annotate_hbars(ax, bars, fmt) -> None:
    pass


def _decorate(ax, title: str, xlabel="", ylabel="") -> None:
    pass


class ConsoleWriter:
    def write(self, records: list[dict]) -> None:
        pass


class GraphicsChartWriter:
    def __init__(self, show_plot: bool = False, save_path: str | None = None) -> None:
        pass

    def write(self, records: list[dict]) -> None:
        pass