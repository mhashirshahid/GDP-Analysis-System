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


def _chart_top_bottom_gdp(records, title, ax):
    data      = _strip(records)
    countries = list(map(lambda r: r.get("country", "?"), data))
    gdps      = list(map(lambda r: float(r.get("gdp") or 0), data))
    colors    = list(map(_bar_color, gdps))
    bars = ax.barh(countries, gdps, color=colors, edgecolor=_P["border"], linewidth=0.5, height=0.7)
    _annotate_hbars(ax, bars, _fmt_gdp)
    _decorate(ax, title, xlabel="GDP (USD)", ylabel="Country")
    ax.invert_yaxis()


def _chart_gdp_growth_rate(records, title, ax):
    data    = _strip(records)
    sorted_ = sorted(data, key=lambda r: float(r.get("growth_rate") or 0), reverse=True)
    countries = list(map(lambda r: r.get("country", "?"), sorted_))
    rates     = list(map(lambda r: float(r.get("growth_rate") or 0), sorted_))
    colors    = list(map(_bar_color, rates))
    bars = ax.barh(countries, rates, color=colors, edgecolor=_P["border"], linewidth=0.5, height=0.7)
    _annotate_hbars(ax, bars, lambda v: f"{v:+.1f}%")
    _decorate(ax, title, xlabel="Overall Growth Rate (%)", ylabel="Country")
    ax.axvline(0, color=_P["border"], linewidth=0.8)
    ax.invert_yaxis()


def _chart_avg_gdp_by_continent(records, title, ax):
    data       = _strip(records)
    continents = list(map(lambda r: r.get("continent", "?"), data))
    avgs       = list(map(lambda r: float(r.get("avg_gdp") or 0), data))
    colors     = _COLORS[:len(continents)]
    bars = ax.bar(continents, avgs, color=colors, edgecolor=_P["border"], linewidth=0.5, width=0.65)

    def _label(bar):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                _fmt_gdp(h), ha="center", va="bottom", color=_P["text"], fontsize=8)
    list(map(_label, bars))
    _decorate(ax, title, xlabel="Continent", ylabel="Average GDP (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_gdp(v)))
    plt.xticks(rotation=20, ha="right")


def _chart_global_gdp_trend(records, title, ax):
    data    = _strip(records)
    sorted_ = sorted(data, key=lambda r: int(r.get("year", 0)))
    years   = list(map(lambda r: int(r.get("year", 0)), sorted_))
    totals  = list(map(lambda r: float(r.get("total_gdp") or 0), sorted_))
    if not years:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center", color=_P["subtext"])
        return
    ax.fill_between(years, totals, alpha=0.15, color=_P["accent"])
    ax.plot(years, totals, color=_P["accent"], linewidth=2.5, marker="o", markersize=4)
    peak = totals.index(max(totals))
    ax.annotate(f"Peak\n{_fmt_gdp(totals[peak])}", xy=(years[peak], totals[peak]),
                xytext=(15, -30), textcoords="offset points", color=_P["positive"], fontsize=8,
                arrowprops=dict(arrowstyle="->", color=_P["positive"]))
    _decorate(ax, title, xlabel="Year", ylabel="Total GDP (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_gdp(v)))
    ax.grid(True, axis="y", alpha=0.3)


def _chart_fastest_continent(records, title, ax):
    data    = _strip(records)
    sorted_ = sorted(data, key=lambda r: float(r.get("growth_pct") or 0), reverse=True)
    conts   = list(map(lambda r: r.get("continent", "?"), sorted_))
    growth  = list(map(lambda r: float(r.get("growth_pct") or 0), sorted_))
    colors  = list(map(_bar_color, growth))
    bars = ax.barh(conts, growth, color=colors, edgecolor=_P["border"], linewidth=0.5, height=0.65)
    _annotate_hbars(ax, bars, lambda v: f"{v:+.1f}%")
    if conts:
        ax.get_yticklabels()[0].set_color(_P["warning"])
        ax.get_yticklabels()[0].set_fontweight("bold")
    _decorate(ax, title, xlabel="GDP Growth (%)", ylabel="Continent")
    ax.invert_yaxis()
    ax.axvline(0, color=_P["border"], linewidth=0.8)


def _chart_consistent_decline(records, title, ax):
    data    = _strip(records)
    sorted_ = sorted(data, key=lambda r: float(r.get("decline_pct") or 0))
    if not sorted_:
        ax.text(0.5, 0.5, "No countries with consistent decline found",
                transform=ax.transAxes, ha="center", color=_P["subtext"], fontsize=10)
        ax.set_title(title, color=_P["text"], fontsize=13, fontweight="bold", pad=14)
        return
    countries = list(map(lambda r: r.get("country", "?"), sorted_))
    declines  = list(map(lambda r: float(r.get("decline_pct") or 0), sorted_))
    bars = ax.barh(countries, declines, color=_P["negative"], edgecolor=_P["border"],
                   linewidth=0.5, height=0.7)
    _annotate_hbars(ax, bars, lambda v: f"{v:.1f}%")
    _decorate(ax, title, xlabel="Total Decline (%)", ylabel="Country")
    ax.invert_yaxis()
    ax.axvline(0, color=_P["border"], linewidth=0.8)


def _chart_continent_contribution(records, title, ax):
    data = _strip(records)
    if not data:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center", color=_P["subtext"])
        return

    def _acc(acc, rec):
        acc.setdefault(int(rec.get("year", 0)), {})[rec.get("continent", "?")] = float(rec.get("share_pct") or 0)
        return acc

    by_year    = reduce(_acc, data, {})
    years      = sorted(by_year.keys())
    continents = sorted(set(chain.from_iterable(map(lambda d: d.keys(), by_year.values()))))
    series     = list(map(lambda c: list(map(lambda yr: by_year[yr].get(c, 0.0), years)), continents))

    ax.stackplot(years, series, labels=continents, colors=_COLORS[:len(continents)], alpha=0.85)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    _decorate(ax, title, xlabel="Year", ylabel="Share of Global GDP (%)")
    ax.legend(fontsize=7, framealpha=0.3, loc="upper left",
              labelcolor=_P["text"], facecolor=_P["surface"], edgecolor=_P["border"])
    ax.grid(True, axis="y", alpha=0.3)


def _chart_default(records, title, ax):
    data   = _strip(records)
    sample = data[0] if data else {}
    lk = next(filter(lambda k: isinstance(sample.get(k), str), sample), None)
    vk = next(filter(lambda k: isinstance(sample.get(k), (int, float)), sample), None)
    if not (lk and vk):
        ax.text(0.5, 0.5, "Cannot render: no label/value keys found",
                transform=ax.transAxes, ha="center", color=_P["subtext"])
        return
    labels = list(map(lambda r: str(r.get(lk, "")), data))
    values = list(map(lambda r: float(r.get(vk) or 0), data))
    ax.bar(labels, values, color=list(map(_bar_color, values)),
           edgecolor=_P["border"], linewidth=0.5, width=0.65)
    _decorate(ax, title)
    plt.xticks(rotation=30, ha="right")


_CHART_DISPATCH = {
    "top_bottom_gdp":         _chart_top_bottom_gdp,
    "gdp_growth_rate":        _chart_gdp_growth_rate,
    "avg_gdp_by_continent":   _chart_avg_gdp_by_continent,
    "global_gdp_trend":       _chart_global_gdp_trend,
    "fastest_continent":      _chart_fastest_continent,
    "consistent_decline":     _chart_consistent_decline,
    "continent_contribution": _chart_continent_contribution,
    "default":                _chart_default,
}


class ConsoleWriter:
    def write(self, records: list[dict]) -> None:
        pass


class GraphicsChartWriter:
    def __init__(self, show_plot: bool = False, save_path: str | None = None) -> None:
        pass

    def write(self, records: list[dict]) -> None:
        pass