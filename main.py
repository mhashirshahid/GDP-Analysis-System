from __future__ import annotations

import logging
import sys
from functools import reduce
from pathlib import Path

from core.config_validator import ConfigError, load, validate
from core.engine import TransformationEngine
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter, GUISink

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger(__name__)

INPUT_DRIVERS  = {"json": JSONReader, "csv": CSVReader}
OUTPUT_DRIVERS = {"console": ConsoleWriter, "chart": GraphicsChartWriter, "gui": GUISink}

_CONFIG_PATH = Path("config.json")


def _build_sink(cfg: dict):
    key  = cfg["output_driver"]
    plot = cfg.get("plot", {})
    kwargs = {
        "chart":   {"show_plot": plot.get("show_plot", False), "save_path": plot.get("save_path")},
        "console": {},
        "gui":     {},
    }.get(key, {})
    return OUTPUT_DRIVERS[key](**kwargs)


def bootstrap() -> None:
    log.info("━━━  GDP Analysis System — Phase 2  ━━━")

    def _load(_):       return load(_CONFIG_PATH)
    def _validate(cfg): return validate(cfg)
    def _wire(cfg):
        sink   = _build_sink(cfg)
        engine = TransformationEngine(sink=sink, config=cfg)
        reader = INPUT_DRIVERS[cfg["input_driver"]](filepath=cfg["data_file"], service=engine)
        return {**cfg, "_sink": sink, "_engine": engine, "_reader": reader}
    def _run(ctx):
        ctx["_reader"].run()
        if isinstance(ctx["_sink"], GUISink):
            ctx["_sink"].launch()
        return ctx

    reduce(lambda acc, fn: fn(acc), [_load, _validate, _wire, _run], None)
    log.info("━━━  Done  ━━━")


def main() -> None:
    debug = "--debug" in sys.argv
    try:
        bootstrap()
    except ConfigError as exc:
        print(f"\n[CONFIG ERROR]\n{exc}\n", file=sys.stderr)
        if debug: raise
        sys.exit(1)
    except RuntimeError as exc:
        print(f"\n[RUNTIME ERROR]\n{exc}\n", file=sys.stderr)
        if debug: raise
        sys.exit(2)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"\n[UNEXPECTED ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
        print("Run with --debug for full traceback.", file=sys.stderr)
        if debug: raise
        sys.exit(3)


if __name__ == "__main__":
    main()