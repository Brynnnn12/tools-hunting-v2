from __future__ import annotations

import argparse
import logging
from pathlib import Path


from rich.console import Console

from core.config import Config
from core.logger import setup_logger
from core.utils import extract_domain, now_timestamp, safe_filename
from modules.classifier import Classifier
from modules.mapper import Mapper
from modules.parser import Parser
from modules.reporter import Reporter
from modules.statistics import Stats
from modules.visualizer import Visualizer

AUTHOR = "brynnnn12"
VERSION = f"AttackSurfaceMapper v1.0 \u2014 {AUTHOR}"

BANNER = """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                                      \u2551
\u2551   BBBB   RRRR   Y   Y  N   N  N   N  N   N  N   N                    \u2551
\u2551   B   B  R   R   Y Y   NN  N  NN  N  NN  N  NN  N                    \u2551
\u2551   BBBB   RRRR     Y    N N N  N N N  N N N  N N N                    \u2551
\u2551   B   B  R  R     Y    N  NN  N  NN  N  NN  N  NN                    \u2551
\u2551   BBBB   R   R    Y    N   N  N   N  N   N  N   N                    \u2551
\u2551                                                                      \u2551
\u2551   AttackSurfaceMapper v1.0  Endpoint classification & graph          \u2551
\u2551   brynnnn12                                                          \u2551
\u2551                                                                      \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="asm.py",
        description="AttackSurfaceMapper v1.0 — classify endpoints, correlate sources, visualize attack surface",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-i", "--input", required=True, help="Input folder from ReconForge/JSHunter")
    parser.add_argument("-o", "--output", help="Output directory (default: reports/)")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    parser.add_argument("--graph", action="store_true", help="Generate graph visualization")
    parser.add_argument("--all", action="store_true", help="Generate all outputs")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def resolve_target(data) -> str:
    for url in list(data.urls)[:10]:
        domain = extract_domain(url)
        if domain:
            return safe_filename(domain)
    return "unknown"


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
        logger = setup_logger("asm")
        logger.info("Starting AttackSurfaceMapper")

        parser_mod = Parser(logger)
        data = parser_mod.parse(input_dir)

        classifier = Classifier()
        categories = classifier.classify(data.endpoints)

        mapper = Mapper(logger)
        mapping = mapper.correlate(data.urls, categories)

        stats = Stats.from_data(data, categories)
        target = resolve_target(data)
        timestamp = now_timestamp()

        generate_all = args.all
        write_json = args.json or generate_all
        write_html = args.html or generate_all
        write_graph = args.graph or generate_all

        graph_path = ""
        if write_graph:
            visualizer = Visualizer(logger)
            graph = visualizer.build_graph(target, mapping)
            graph_file = reports_dir / "attack_surface.png"
            visualizer.render(graph, graph_file)
            graph_path = graph_file.name

        reporter = Reporter(reports_dir, logger)
        reporter.generate_reports(
            target=target,
            stats=stats,
            categories=categories,
            mapping=mapping,
            timestamp=timestamp,
            graph_path=graph_path,
            secrets=data.secrets,
            write_json=write_json,
            write_html=write_html,
        )

        console.print(f"[green]Done.[/green] Reports: {reports_dir}")
        return 0
    except Exception as exc:
        logging.exception("AttackSurfaceMapper failed")
        print(f"\n  [red]Error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
