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
    rc = {
        "figure.facecolor": _P["bg"],  "axes.facecolor":  _P["surface"],
        "axes.edgecolor":   _P["border"], "axes.labelcolor": _P["text"],
        "xtick.color":      _P["subtext"], "ytick.color":   _P["subtext"],
        "text.color":       _P["text"],   "grid.color":     _P["border"],
        "grid.linestyle":   "--",          "grid.linewidth": 0.5,
        "font.family":      "DejaVu Sans",
        "axes.spines.top":  False,         "axes.spines.right": False,
    }
    list(map(lambda kv: plt.rcParams.update({kv[0]: kv[1]}), rc.items()))
    fig.set_facecolor(_P["bg"])
    return fig


def _meta(records: list[dict], key: str, default: Any = None) -> Any:
    return records[0].get(key, default) if records else default


def _strip(records: list[dict]) -> list[dict]:
    return list(map(lambda r: dict(filter(lambda kv: not kv[0].startswith("_"), r.items())), records))


def _fmt_gdp(v: float) -> str:
    a = abs(v)
    if a >= 1e12: return f"${v/1e12:.2f} T"
    if a >= 1e9:  return f"${v/1e9:.2f} B"
    if a >= 1e6:  return f"${v/1e6:.2f} M"
    return f"${v:,.0f}"


def _bar_color(v: float) -> str:
    return _P["positive"] if v >= 0 else _P["negative"]


def _annotate_hbars(ax, bars, fmt) -> None:
    def _one(bar):
        w = bar.get_width()
        ax.text(w + abs(w) * 0.01, bar.get_y() + bar.get_height() / 2,
                fmt(w), va="center", ha="left", color=_P["text"], fontsize=8)
    list(map(_one, bars))


def _decorate(ax, title: str, xlabel="", ylabel="") -> None:
    ax.set_title(title, color=_P["text"], fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel(xlabel, color=_P["subtext"], fontsize=9)
    ax.set_ylabel(ylabel, color=_P["subtext"], fontsize=9)
    ax.grid(True, axis="x", alpha=0.3)


class ConsoleWriter:
    def write(self, records: list[dict]) -> None:
        pass


class GraphicsChartWriter:
    def __init__(self, show_plot: bool = False, save_path: str | None = None) -> None:
        pass

    def write(self, records: list[dict]) -> None:
        pass