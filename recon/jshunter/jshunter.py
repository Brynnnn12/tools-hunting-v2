from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from rich.console import Console

from core.config import Config
from core.logger import setup_logger
from core.utils import (
    dedupe_preserve_order,
    ensure_dir,
    extract_domain,
    find_js_files_local,
    find_js_urls_from_reconforge,
    normalize_url,
    now_timestamp,
    read_lines,
    safe_filename,
)
from modules.analyzer import Analyzer
from modules.downloader import Downloader
from modules.reporter import Reporter
from modules.statistics import Stats


AUTHOR = "brynnnn12"

BANNER = f"""
     _ ____  _   _             _
    | / ___|| | | |_   _ _ __ | |_ ___ _ __
 _  | \\___ \\| |_| | | | | '_ \\| __/ _ \\ '__|
| |_| |___) |  _  | |_| | | | | ||  __/ |
 \\___/|____/|_| |_|\\__,_|_| |_|\\__\\___|_|

JavaScript Intelligence Framework  v1.0  —  {AUTHOR}
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jshunter.py",
        usage="jshunter.py [options]",
        description="JSHunter v1.0\n\nJavaScript Intelligence Framework",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    parser.add_argument("-u", "--url", help="Single JavaScript URL")
    parser.add_argument("-f", "--file", help="File containing JavaScript URLs")
    parser.add_argument("-i", "--input", help="ReconForge output directory (auto-find JS URLs)")
    parser.add_argument("-d", "--dir", help="Scan local .js files in directory recursively")
    parser.add_argument("-o", "--output", help="Output directory", default=None)
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--threads", type=int, help="Number of download threads")
    parser.add_argument("--version", action="version", version=f"JSHunter v1.0 — {AUTHOR}")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser


def resolve_target(urls: List[str]) -> str:
    domains = {extract_domain(url) for url in urls if extract_domain(url)}
    if len(domains) == 1:
        return safe_filename(next(iter(domains)))
    return "mixed"


def read_local_js(dir_path: Path) -> dict:
    from modules.analyzer import Analyzer
    contents: dict = {}
    files = find_js_files_local(dir_path)
    for fp in files:
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
            if text.strip():
                contents[str(fp)] = text
        except Exception:
            pass
    return contents


def main() -> int:
    config = Config()
    console = Console()
    console.print(BANNER, style="bold cyan")

    parser = build_parser()
    args = parser.parse_args()

    if not args.url and not args.file and not args.input and not args.dir:
        parser.print_help()
        return 1

    urls: List[str] = []
    if args.url:
        urls.append(normalize_url(args.url))
    if args.file:
        try:
            urls.extend(read_lines(Path(args.file)))
        except (FileNotFoundError, PermissionError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            return 1
    if args.input:
        input_dir = Path(args.input).resolve()
        if not input_dir.exists():
            console.print(f"[red]Error:[/red] Input directory not found: {input_dir}")
            return 1
        found = find_js_urls_from_reconforge(input_dir)
        if found:
            console.print(f"[dim]Found {len(found)} JS URLs from {input_dir.name}[/dim]")
            urls.extend(sorted(found))
        else:
            console.print("[yellow]No JS URLs found in ReconForge output[/yellow]")

    urls = dedupe_preserve_order([normalize_url(url) for url in urls])

    output_root = Path(args.output) if args.output else config.output_dir
    ensure_dir(output_root)

    logger = setup_logger(config.log_file)
    logger.info("Starting JSHunter")

    contents: dict = {}

    if args.dir:
        js_dir = Path(args.dir).resolve()
        if not js_dir.exists():
            console.print(f"[red]Error:[/red] Directory not found: {js_dir}")
            return 1
        console.print(f"[dim]Scanning local JS files in {js_dir}[/dim]")
        contents = read_local_js(js_dir)
        if not contents:
            console.print("[red]Error:[/red] No .js files found in directory")
            return 1
        console.print(f"[dim]Loaded {len(contents)} JS files[/dim]")
        logger.info("Loaded %d local JS files", len(contents))

    if urls:
        threads = args.threads or config.default_threads
        downloader = Downloader(config.timeout, config.user_agent, logger)
        logger.info("Downloading %d JS files", len(urls))
        downloaded = downloader.download_many(urls, threads)
        console.print(f"[dim]Downloaded {len(downloaded)}/{len(urls)} JS files[/dim]")
        contents.update(downloaded)

    if not contents:
        logger.error("No JavaScript content to analyze")
        console.print("[red]Error:[/red] No JavaScript content to analyze")
        return 1

    analyzer = Analyzer(logger)
    results = analyzer.analyze(contents)

    stats = Stats.from_results(contents.keys(), results)
    timestamp = now_timestamp()

    write_json = args.json or (not args.json and not args.html)
    write_html = args.html or (not args.json and not args.html)

    reporter = Reporter(output_root, logger)
    reporter.write_outputs(
        target=resolve_target(list(contents.keys())),
        results=results,
        stats=stats,
        timestamp=timestamp,
        write_json=write_json,
        write_html=write_html,
    )

    console.print("[green]Done.[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
