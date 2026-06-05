from __future__ import annotations

import argparse
import logging
from pathlib import Path

from rich.console import Console

from core.config import Config
from core.logger import setup_logger
from core.utils import now_timestamp
from modules.aggregator import Aggregator
from modules.dashboard import DashboardBuilder
from modules.parser import Parser
from modules.reporter import Reporter
from modules.statistics import Stats
from modules.visualizer import Visualizer

AUTHOR = "brynnnn12"
VERSION = f"ReportHub v1.0 \u2014 {AUTHOR}"

BANNER = f"""
 ____                       _   _       _
|  _ \\ ___ _ __   ___  _ __| |_| |_   _| |__
| |_) / _ \\ '_ \\ / _ \\| '__| __| | | | | '_ \\
|  _ <  __/ |_) | (_) | |  | |_| | |_| | |_) |
|_| \\_\\___| .__/ \\___/|_|   \\__|_|\\__,_|_.__/
          |_|

ReportHub  v1.0  \u2014  {AUTHOR}
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reporthub.py",
        description="ReportHub v1.0 — Unified Reporting Engine",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-i", "--input", required=True, help="Input folder for target output")
    parser.add_argument("-o", "--output", help="Output directory (default: reports/)")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    parser.add_argument("--dashboard", action="store_true", help="Generate dashboard")
    parser.add_argument("--all", action="store_true", help="Generate all outputs")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def main() -> int:
    try:
        console = Console()
        console.print(BANNER, style="bold cyan")

        config = Config()
        args = build_parser().parse_args()

        input_dir = Path(args.input)
        if not input_dir.exists():
            console.print("[red]Error:[/red] Input directory not found")
            return 1

        reports_dir = Path(args.output).resolve() if args.output else config.reports_dir
        logger = setup_logger(config.log_file, name="reporthub")
        logger.info("Starting ReportHub for: %s", input_dir.name)

        parser_mod = Parser(logger)
        raw_data = parser_mod.parse(input_dir)

        aggregator = Aggregator(logger)
        data = aggregator.aggregate(raw_data)

        stats = Stats.from_data(data)
        timestamp = now_timestamp()

        generate_all = args.all
        include_html = args.html or generate_all
        include_json = args.json or generate_all
        include_dashboard = args.dashboard or generate_all

        visualizer = Visualizer(logger)
        charts = visualizer.generate(data.get("categories", {}), data.get("frameworks", []), reports_dir)

        dashboard_builder = DashboardBuilder(logger)
        dashboard_snippets = dashboard_builder.build_charts(data.get("categories", {}), data.get("frameworks", []))

        reporter = Reporter(reports_dir, logger)
        reporter.generate(
            target=input_dir.name,
            timestamp=timestamp,
            stats=stats,
            data=data,
            charts=charts,
            dashboard_snippets=dashboard_snippets,
            include_html=include_html,
            include_dashboard=include_dashboard,
            include_json=include_json,
        )

        console.print("[green]Done.[/green]")
        return 0
    except Exception as exc:
        logging.exception("ReportHub failed")
        print(f"\n  [red]Error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
