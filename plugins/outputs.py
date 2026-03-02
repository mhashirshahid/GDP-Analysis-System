from __future__ import annotations

import logging
from functools import reduce
from itertools import chain
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure

log = logging.getLogger(__name__)

_SEP = "─" * 72

# Per-chart personality themes

_T = {
    # Warm gold gradient
    "hall_of_fame": {
        "bg": "#0d0900", "surface": "#171000",
        "bar_colors": [
            "#FFD700", "#D4D4D4", "#CD7F32",
            "#E8A030", "#D49030", "#BF8030", "#AA7030",
            "#956030", "#805030", "#6B4030",
        ],
        "text": "#FFF3C0", "subtext": "#AA8830",
        "accent": "#FFD700", "grid": "#2a1e00",
        "spine": "#FFD700", "title": "#FFD700",
    },
    # Deep ice blues
    "the_cellar": {
        "bg": "#000b16", "surface": "#001428",
        "bar_colors": [
            "#00BFFF", "#009EDD", "#007DBB", "#005C99",
            "#003B77", "#001A55", "#002266", "#001144",
            "#000F33", "#000A22",
        ],
        "text": "#B0D8FF", "subtext": "#2A6080",
        "accent": "#00BFFF", "grid": "#001c30",
        "spine": "#00BFFF", "title": "#55CCFF",
    },
    # Forest green/red 
    "the_race": {
        "bg": "#020e06", "surface": "#041808",
        "pos": "#00E676", "neg": "#FF1744",
        "text": "#B0FFD8", "subtext": "#3A7055",
        "accent": "#00E676", "grid": "#082016",
        "spine": "#00E676", "title": "#00FF88",
    },
    # Earth-toned colors
    "around_the_world": {
        "bg": "#070605", "surface": "#100e0a",
        "continent_colors": {
            "Africa":         "#F4A460",
            "Asia":           "#4ECDC4",
            "Europe":         "#5588DD",
            "North America": "#3CB371",
            "South America": "#FF7043",
            "Oceania":        "#26C6DA",
            "Global":         "#AB47BC",
        },
        "fallback": ["#F4A460","#4ECDC4","#5588DD","#3CB371","#FF7043","#26C6DA","#AB47BC"],
        "text": "#E8DCC8", "subtext": "#7A6A5A",
        "accent": "#C8A46E", "grid": "#181510",
        "spine": "#C8A46E", "title": "#DEB887",
    },
    # Deep space cyan glow
    "cosmic": {
        "bg": "#010012", "surface": "#040030",
        "line": "#00FFFF", "fill": "#00FFFF",
        "text": "#C0D0FF", "subtext": "#3A4880",
        "accent": "#00FFFF", "grid": "#080830",
        "spine": "#00FFFF", "title": "#00FFFF",
    },
    # Ember orange fire
    "podium": {
        "bg": "#0d0400", "surface": "#1a0800",
        "winner": "#FF4500", "others": "#3A2010",
        "text": "#FFD0A0", "subtext": "#7A4030",
        "accent": "#FF6A00", "grid": "#200a00",
        "spine": "#FF4500", "title": "#FF6A00",
    },
    # Blood red  
    "red_alert": {
        "bg": "#0d0000", "surface": "#1a0000",
        "bar": "#CC2200",
        "text": "#FFB0B0", "subtext": "#7A2020",
        "accent": "#FF3030", "grid": "#2a0000",
        "spine": "#CC2200", "title": "#FF4444",
    },
    # Vibrant palette
    "symphony": {
        "bg": "#010308", "surface": "#030610",
        "colors": ["#FF6B6B","#4ECDC4","#FFE66D","#A8E6CF","#FF8B94","#B8B8FF","#FFDAC1"],
        "text": "#F0F0FF", "subtext": "#5060A0",
        "accent": "#FF6B6B", "grid": "#06080f",
        "spine": "#FF6B6B", "title": "#FF8080",
    },
}


# Shared utilities

def _meta(records: list[dict], key: str, default: Any = None) -> Any:
    return records[0].get(key, default) if records else default


def _strip(records: list[dict]) -> list[dict]:
    return list(map(
        lambda r: dict(filter(lambda kv: not kv[0].startswith("_"), r.items())),
        records,
    ))


def _fmt_gdp(v: float) -> str:
    a = abs(v)
    if a >= 1e12: return f"${v/1e12:.2f}T"
    if a >= 1e9:  return f"${v/1e9:.2f}B"
    if a >= 1e6:  return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"


def _apply_theme(fig: Figure, t: dict) -> None:
    rc = {
        "figure.facecolor":  t["bg"],
        "axes.facecolor":    t["surface"],
        "axes.edgecolor":    t.get("spine", t["accent"]),
        "axes.labelcolor":   t["text"],
        "xtick.color":       t["subtext"],
        "ytick.color":       t["subtext"],
        "text.color":        t["text"],
        "grid.color":        t["grid"],
        "grid.linestyle":    "--",
        "grid.linewidth":    0.5,
        "font.family":       "DejaVu Sans",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    }
    list(map(lambda kv: plt.rcParams.update({kv[0]: kv[1]}), rc.items()))
    fig.set_facecolor(t["bg"])


def _accent_spines(ax, t: dict) -> None:
    ax.spines["left"].set_color(t["spine"])
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_color(t.get("subtext", t["spine"]))
    ax.spines["bottom"].set_linewidth(0.8)


def _set_title(ax, icon: str, text: str, t: dict) -> None:
    ax.set_title(f"{icon}  {text}", color=t["title"],
                 fontsize=13, fontweight="bold", pad=16, loc="left")


def _annotate_hbars(ax, bars, fmt, color: str) -> None:
    xlim = ax.get_xlim()
    pad  = (xlim[1] - xlim[0]) * 0.012
    def _one(bar):
        w = bar.get_width()
        ax.text(w + pad, bar.get_y() + bar.get_height() / 2,
                fmt(w), va="center", ha="left",
                color=color, fontsize=8, fontweight="bold")
    list(map(_one, bars))


def _watermark(ax, text: str, t: dict) -> None:
    ax.text(0.97, 0.04, text, transform=ax.transAxes,
            color=t["accent"], fontsize=30, alpha=0.05,
            ha="right", va="bottom", fontweight="bold")


# Chart renderers

def _chart_top_bottom_gdp(records: list[dict], title: str, ax) -> None:
    rank = _meta(records, "rank_label", "TOP")
    t    = _T["hall_of_fame"] if rank == "TOP" else _T["the_cellar"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])
    _accent_spines(ax, t)

    countries = list(map(lambda r: r.get("country", "?"), data))
    gdps      = list(map(lambda r: float(r.get("gdp") or 0), data))
    n         = len(t["bar_colors"])
    colors    = list(map(lambda i: t["bar_colors"][min(i, n - 1)], range(len(data))))

    bars = ax.barh(countries, gdps, color=colors,
                    edgecolor="none", height=0.72, linewidth=0)
    _annotate_hbars(ax, bars, _fmt_gdp, t["text"])

    icon = "TOP" if rank == "TOP" else "BOTTOM"
    _set_title(ax, icon, title, t)
    ax.set_xlabel("GDP (USD)", color=t["subtext"], fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_gdp(v)))
    ax.grid(True, axis="x", alpha=0.2)
    ax.tick_params(axis="y", colors=t["subtext"])
    ax.invert_yaxis()
    _watermark(ax, "GDP", t)


def _chart_gdp_growth_rate(records: list[dict], title: str, ax) -> None:
    t    = _T["the_race"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])
    _accent_spines(ax, t)

    sorted_   = sorted(data, key=lambda r: float(r.get("growth_rate") or 0), reverse=True)
    countries = list(map(lambda r: r.get("country", "?"), sorted_))
    rates     = list(map(lambda r: float(r.get("growth_rate") or 0), sorted_))
    colors    = list(map(lambda v: t["pos"] if v >= 0 else t["neg"], rates))

    bars = ax.barh(countries, rates, color=colors,
                    edgecolor="none", height=0.72, linewidth=0)
    _annotate_hbars(ax, bars, lambda v: f"{v:+.1f}%", t["text"])

    ax.axvline(0, color=t["text"], linewidth=2.0, alpha=0.35, zorder=5)

    _set_title(ax, "RACE", title, t)
    ax.set_xlabel("Overall Growth Rate (%)", color=t["subtext"], fontsize=9)
    ax.grid(True, axis="x", alpha=0.15)
    ax.invert_yaxis()
    _watermark(ax, "%", t)


def _chart_avg_gdp_by_continent(records: list[dict], title: str, ax) -> None:
    t    = _T["around_the_world"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])
    _accent_spines(ax, t)

    sorted_ = sorted(data, key=lambda r: float(r.get("avg_gdp") or 0), reverse=True)
    conts   = list(map(lambda r: r.get("continent", "?"), sorted_))
    avgs    = list(map(lambda r: float(r.get("avg_gdp") or 0), sorted_))
    fb      = t["fallback"]
    colors  = list(map(
        lambda c: t["continent_colors"].get(c, fb[hash(c) % len(fb)]),
        conts,
    ))

    bars = ax.bar(conts, avgs, color=colors,
                  edgecolor="none", width=0.65, linewidth=0)

    def _label(pair):
        bar, v = pair
        ax.text(bar.get_x() + bar.get_width() / 2,
                v * 1.01, _fmt_gdp(v),
                ha="center", va="bottom",
                color=t["text"], fontsize=8, fontweight="bold")
    list(map(_label, zip(bars, avgs)))

    _set_title(ax, "WORLD", title, t)
    ax.set_xlabel("Continent", color=t["subtext"], fontsize=9)
    ax.set_ylabel("Average GDP (USD)", color=t["subtext"], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_gdp(v)))
    ax.grid(True, axis="y", alpha=0.2)
    plt.xticks(rotation=20, ha="right")
    _watermark(ax, "AVG", t)


def _chart_global_gdp_trend(records: list[dict], title: str, ax) -> None:
    t    = _T["cosmic"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])
    _accent_spines(ax, t)

    if not data:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                ha="center", color=t["subtext"], fontsize=12)
        return

    sorted_ = sorted(data, key=lambda r: int(r.get("year", 0)))
    years   = list(map(lambda r: int(r.get("year", 0)), sorted_))
    totals  = list(map(lambda r: float(r.get("total_gdp") or 0), sorted_))

    # layered glow — three fill passes + two line passes
    ax.fill_between(years, totals, alpha=0.04, color=t["fill"])
    ax.fill_between(years, totals, alpha=0.08, color=t["fill"])
    ax.fill_between(years, totals, alpha=0.13, color=t["fill"])
    ax.plot(years, totals, color=t["line"], linewidth=8,  alpha=0.08)
    ax.plot(years, totals, color=t["line"], linewidth=3,  alpha=0.40)
    ax.plot(years, totals, color=t["line"], linewidth=1.5,
            marker="o", markersize=4,
            markerfacecolor=t["line"],
            markeredgecolor=t["bg"], markeredgewidth=1.5)

    peak = totals.index(max(totals))
    ax.annotate(
        f"  Peak\n  {_fmt_gdp(totals[peak])}",
        xy=(years[peak], totals[peak]),
        xytext=(22, -48), textcoords="offset points",
        color=t["accent"], fontsize=8, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=t["accent"], lw=1.5),
    )

    _set_title(ax, "COSMIC", title, t)
    ax.set_xlabel("Year", color=t["subtext"], fontsize=9)
    ax.set_ylabel("Total GDP (USD)", color=t["subtext"], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_gdp(v)))
    ax.grid(True, alpha=0.12)
    _watermark(ax, "inf", t)


def _chart_fastest_continent(records: list[dict], title: str, ax) -> None:
    t    = _T["podium"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])
    _accent_spines(ax, t)

    sorted_    = sorted(data, key=lambda r: float(r.get("growth_pct") or 0), reverse=True)
    conts      = list(map(lambda r: r.get("continent", "?"), sorted_))
    growth     = list(map(lambda r: float(r.get("growth_pct") or 0), sorted_))
    is_fastest = list(map(lambda r: r.get("is_fastest", False), sorted_))

    colors  = list(map(lambda f: t["winner"] if f else t["others"], is_fastest))
    heights = list(map(lambda f: 0.85 if f else 0.60, is_fastest))

    bars = ax.barh(conts, growth, color=colors,
                    edgecolor="none", height=heights, linewidth=0)

    def _label(pair):
        bar, fastest = pair
        w   = bar.get_width()
        xlim = ax.get_xlim()
        pad  = (xlim[1] - xlim[0]) * 0.012
        suffix = "  CHAMPION" if fastest else ""
        ax.text(w + pad, bar.get_y() + bar.get_height() / 2,
                f"{w:+.1f}%{suffix}",
                va="center", ha="left",
                color=t["winner"] if fastest else t["text"],
                fontsize=9 if fastest else 8,
                fontweight="bold" if fastest else "normal")
    list(map(_label, zip(bars, is_fastest)))

    ax.axvline(0, color=t["text"], linewidth=1, alpha=0.3)
    _set_title(ax, "PODIUM", title, t)
    ax.set_xlabel("GDP Growth (%)", color=t["subtext"], fontsize=9)
    ax.grid(True, axis="x", alpha=0.12)
    ax.invert_yaxis()
    _watermark(ax, "WIN", t)


def _chart_consistent_decline(records: list[dict], title: str, ax) -> None:
    t    = _T["red_alert"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])

    # full warning border on all four sides
    list(map(lambda s: (
        ax.spines[s].set_visible(True),
        ax.spines[s].set_color(t["spine"]),
        ax.spines[s].set_linewidth(2.5),
    ), ["left", "right", "top", "bottom"]))

    if not data:
        ax.text(0.5, 0.5, "No countries with consistent decline",
                transform=ax.transAxes, ha="center",
                color="#00DD66", fontsize=12, fontweight="bold")
        ax.set_title(f"WARNING  {title}", color=t["title"],
                     fontsize=13, fontweight="bold", pad=16, loc="left")
        return

    sorted_   = sorted(data, key=lambda r: float(r.get("decline_pct") or 0))
    countries = list(map(lambda r: r.get("country", "?"), sorted_))
    declines  = list(map(lambda r: float(r.get("decline_pct") or 0), sorted_))

    max_dec    = abs(min(declines)) if declines else 1.0
    intensities = list(map(lambda v: 0.40 + 0.60 * abs(v) / max_dec, declines))
    bar_colors  = list(map(lambda i: (i, 0.0, 0.04), intensities))

    bars = ax.barh(countries, declines, color=bar_colors,
                    edgecolor="none", height=0.72, linewidth=0)
    _annotate_hbars(ax, bars, lambda v: f"{v:.1f}%", t["text"])

    ax.axvline(0, color=t["accent"], linewidth=1, alpha=0.5)
    _set_title(ax, "WARNING", title, t)
    ax.set_xlabel("Total Decline (%)", color=t["subtext"], fontsize=9)
    ax.grid(True, axis="x", alpha=0.15)
    ax.invert_yaxis()
    _watermark(ax, "ALERT", t)


def _chart_continent_contribution(records: list[dict], title: str, ax) -> None:
    t    = _T["symphony"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])
    _accent_spines(ax, t)

    if not data:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                ha="center", color=t["subtext"])
        return

    def _acc(acc, rec):
        acc.setdefault(int(rec.get("year", 0)), {})[rec.get("continent", "?")] = \
            float(rec.get("share_pct") or 0)
        return acc

    by_year    = reduce(_acc, data, {})
    years      = sorted(by_year.keys())
    continents = sorted(set(chain.from_iterable(
        map(lambda d: d.keys(), by_year.values())
    )))
    series = list(map(
        lambda c: list(map(lambda yr: by_year[yr].get(c, 0.0), years)),
        continents,
    ))

    ax.stackplot(years, series, labels=continents,
                  colors=t["colors"][:len(continents)], alpha=0.88)

    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    _set_title(ax, "SYMPHONY", title, t)
    ax.set_xlabel("Year", color=t["subtext"], fontsize=9)
    ax.set_ylabel("Share of Global GDP (%)", color=t["subtext"], fontsize=9)
    ax.legend(fontsize=7, framealpha=0.25, loc="upper left",
              labelcolor=t["text"], facecolor=t["surface"],
              edgecolor=t["accent"])
    ax.grid(True, axis="y", alpha=0.15)
    _watermark(ax, "100%", t)


def _chart_default(records: list[dict], title: str, ax) -> None:
    t    = _T["around_the_world"]
    data = _strip(records)

    _apply_theme(ax.get_figure(), t)
    ax.set_facecolor(t["surface"])

    sample = data[0] if data else {}
    lk = next(filter(lambda k: isinstance(sample.get(k), str), sample), None)
    vk = next(filter(lambda k: isinstance(sample.get(k), (int, float)), sample), None)
    if not (lk and vk):
        ax.text(0.5, 0.5, "Cannot render: no label/value keys found",
                transform=ax.transAxes, ha="center", color=t["subtext"])
        return

    labels = list(map(lambda r: str(r.get(lk, "")), data))
    values = list(map(lambda r: float(r.get(vk) or 0), data))
    ax.bar(labels, values, color=t["fallback"][0], edgecolor="none", width=0.65)
    ax.set_title(title, color=t["title"], fontsize=13,
                  fontweight="bold", pad=16, loc="left")
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


# Console writer

class ConsoleWriter:
    def write(self, records: list[dict]) -> None:
        if not records:
            return
        chart_type = _meta(records, "_chart_type", "default")
        title      = _meta(records, "_title", "RESULT")
        clean      = _strip(records)

        _BODY = {
            "top_bottom_gdp":         self._fmt_top_bottom,
            "gdp_growth_rate":        self._fmt_growth_rate,
            "avg_gdp_by_continent":   self._fmt_avg_continent,
            "global_gdp_trend":       self._fmt_global_trend,
            "fastest_continent":      self._fmt_fastest,
            "consistent_decline":     self._fmt_decline,
            "continent_contribution": self._fmt_contribution,
        }
        renderer = _BODY.get(chart_type, self._fmt_generic)
        print(f"\n{_SEP}\n  {title}\n{_SEP}")
        list(map(renderer, clean))
        print(f"{_SEP}\n  {len(clean)} record(s)\n{_SEP}\n")

    @staticmethod
    def _fmt_top_bottom(r):
        print(f"  [{r.get('rank_label',''):6s}]  {r.get('country','?'):<40s}  {_fmt_gdp(float(r.get('gdp') or 0)):>14s}")

    @staticmethod
    def _fmt_growth_rate(r):
        rate = float(r.get("growth_rate") or 0)
        print(f"  {'UP' if rate >= 0 else 'DOWN'}  {r.get('country','?'):<35s}  {rate:+.2f}%")

    @staticmethod
    def _fmt_avg_continent(r):
        print(f"  {r.get('continent','?'):<25s}  {_fmt_gdp(float(r.get('avg_gdp') or 0)):>14s}")

    @staticmethod
    def _fmt_global_trend(r):
        print(f"  {r.get('year','?')}  ->  {_fmt_gdp(float(r.get('total_gdp') or 0)):>16s}")

    @staticmethod
    def _fmt_fastest(r):
        star = " FASTEST" if r.get("is_fastest") else ""
        print(f"  {r.get('continent','?'):<25s}  {float(r.get('growth_pct') or 0):+.2f}%{star}")

    @staticmethod
    def _fmt_decline(r):
        print(f"  {r.get('country','?'):<35s}  {float(r.get('decline_pct') or 0):.1f}% over {r.get('decline_years','?')} yr(s)")

    @staticmethod
    def _fmt_contribution(r):
        pct = float(r.get("share_pct") or 0)
        print(f"  {r.get('year','?')}  {r.get('continent','?'):<20s}  {'#' * int(pct/3):<20s}  {pct:.1f}%")

    @staticmethod
    def _fmt_generic(r):
        print("  " + "  |  ".join(map(lambda kv: f"{kv[0]}: {kv[1]}", r.items())))


# Graphics chart writer

class GraphicsChartWriter:
    def __init__(self, show_plot: bool = False, save_path: str | None = None) -> None:
        self._show = show_plot
        self._save = save_path

    def write(self, records: list[dict]) -> None:
        if not records:
            log.warning("GraphicsChartWriter: empty records — skipping.")
            return
        chart_type = _meta(records, "_chart_type", "default")
        title      = _meta(records, "_title", "GDP Analysis")
        renderer   = _CHART_DISPATCH.get(chart_type, _CHART_DISPATCH["default"])

        rank = _meta(records, "rank_label", "")
        save_key = (
            "top_10_gdp"    if (chart_type == "top_bottom_gdp" and rank == "TOP")    else
            "bottom_10_gdp" if (chart_type == "top_bottom_gdp" and rank == "BOTTOM") else
            chart_type
        )

        try:
            fig, ax = plt.subplots(figsize=(14, 7))
            renderer(records, title, ax)
            self._finalise(fig, save_key)
        except Exception as exc:
            plt.close("all")
            raise RuntimeError(f"Chart render failed for '{chart_type}': {exc}") from exc

    def _finalise(self, fig, chart_type: str) -> None:
        fig.tight_layout(pad=2.0)
        if self._save:
            path = self._save_path(chart_type)
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, dpi=150,
                        facecolor=fig.get_facecolor(),
                        bbox_inches="tight")
            log.info("Saved -> %s", path)
        if self._show:
            plt.show()
        plt.close(fig)

    def _save_path(self, chart_type: str) -> Path:
        base = Path(self._save)
        return base.parent / f"{base.stem}_{chart_type}{base.suffix}"


# GUI sink

class GUISink:
    def __init__(self) -> None:
        self._figures: list[tuple] = []

    def write(self, records: list[dict]) -> None:
        if not records:
            return
        chart_type = _meta(records, "_chart_type", "default")
        title      = _meta(records, "_title", "GDP Analysis")
        renderer   = _CHART_DISPATCH.get(chart_type, _CHART_DISPATCH["default"])

        fig, ax = plt.subplots(figsize=(14, 7))
        renderer(records, title, ax)
        fig.tight_layout(pad=2.0)
        self._figures.append((title, fig))

    def launch(self) -> None:
        from GUI.dashboard import GUIDashboard
        GUIDashboard(self._figures).mainloop()