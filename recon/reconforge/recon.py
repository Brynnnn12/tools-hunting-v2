from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from core.config import AppConfig
from core.logger import setup_logger
from core.utils import ensure_dir, normalize_domain, write_json, write_text
from modules.hosts import HostsModule
from modules.reports import ReportModule
from modules.subdomains import SubdomainModule
from modules.urls import UrlsModule
from modules.whois import WhoIsModule

BANNER = f"""
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                                      \u2551
\u2551   BBBB   RRRR   Y   Y  N   N  N   N  N   N  N   N                    \u2551
\u2551   B   B  R   R   Y Y   NN  N  NN  N  NN  N  NN  N                    \u2551
\u2551   BBBB   RRRR     Y    N N N  N N N  N N N  N N N                    \u2551
\u2551   B   B  R  R     Y    N  NN  N  NN  N  NN  N  NN                    \u2551
\u2551   BBBB   R   R    Y    N   N  N   N  N   N  N   N                    \u2551
\u2551                                                                      \u2551
\u2551   ReconForge v{{VERSION:<5}}  Subdomains / Hosts / URLs / Whois      \u2551
\u2551   {{AUTHOR}}                                                         \u2551
\u2551                                                                      \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""

VERSION = "0.2.0"
AUTHOR = "brynnnn12"


class ReconForgeApp:
    def __init__(self, config: AppConfig, console: Console) -> None:
        self.config = config
        self.console = console
        self.logger = setup_logger("reconforge")

    def run(self, modules: List[object], run_report: bool) -> int:
        if not modules and not run_report:
            self.console.print("[bold red]No modules selected.[/bold red]")
            return 2

        ensure_dir(self.config.output_dir)
        results: Dict[str, List[str]] = {}

        self.logger.info("Starting ReconForge for domain: %s", self.config.domain)

        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task_id = progress.add_task("Running modules", total=len(modules))
            for module in modules:
                module_name = getattr(module, "name", module.__class__.__name__)
                progress.update(task_id, description=f"Running {module_name}")
                try:
                    items = module.run()
                    results[module_name] = items
                    self.logger.info("%s: %d items", module_name, len(items))
                except Exception as exc:
                    self.logger.exception("Module failed: %s", module_name)
                    self.console.print(
                        f"[bold yellow]Warning[/bold yellow]: {module_name} failed: {exc}"
                    )
                progress.advance(task_id)

        for name, items in results.items():
            content = "\n".join(items) + ("\n" if items else "")
            write_text(self.config.output_dir / f"{name}.txt", content)
            if self.config.json_enabled:
                write_json(self.config.output_dir / f"{name}.json", {"items": items})

        summary = {name: len(items) for name, items in results.items()}

        if run_report:
            report = ReportModule(self.config.domain, self.config.output_dir)
            report.write(results, summary, self.config.json_enabled, self.config.html_enabled)

        self._print_summary(summary)
        self.console.print(
            f"\n[bold green]Done![/bold green] Output saved to: "
            f"[underline]{self.config.output_dir}[/underline]"
        )
        self.logger.info("ReconForge completed")
        return 0

    def _print_summary(self, summary: Dict[str, int]) -> None:
        table = Table(title="ReconForge Summary", header_style="bold cyan")
        table.add_column("Module", style="bold")
        table.add_column("Count", justify="right")

        for name, count in summary.items():
            table.add_row(name, str(count))

        total = sum(summary.values())
        table.add_row("Total", str(total), style="bold")
        self.console.print(table)


def build_parser() -> argparse.ArgumentParser:
    description = (
        "ReconForge is a recon OSINT and asset management framework for authorized targets.\n"
        "It organizes outputs for subdomains, hosts, and URLs with structured reporting."
    )
    epilog = (
        "Examples:\n"
        "  python recon.py -d example.com --all\n"
        "  python recon.py -d example.com --subdomains\n"
        "  python recon.py -d example.com --hosts\n"
        "  python recon.py -d example.com --urls\n"
        "  python recon.py -d example.com --report"
    )

    parser = argparse.ArgumentParser(
        prog="recon.py",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-d",
        "--domain",
        help="Target domain (authorized scope only)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory root (default: output)",
    )
    parser.add_argument("--all", action="store_true", help="Run all modules")
    parser.add_argument("--subdomains", action="store_true", help="Collect subdomains")
    parser.add_argument("--hosts", action="store_true", help="Collect hosts")
    parser.add_argument("--urls", action="store_true", help="Collect URLs")
    parser.add_argument("--whois", action="store_true", help="Whois lookup")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--json", action="store_true", help="Export JSON alongside TXT")
    parser.add_argument("--html", action="store_true", help="Export HTML report")
    parser.add_argument("--version", action="version", version=f"ReconForge v{VERSION} by {AUTHOR}")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.domain:
        parser.error("The following arguments are required: -d/--domain")

    domain = normalize_domain(args.domain)
    output_root = Path(args.output).expanduser().resolve()
    output_dir = output_root / domain

    config = AppConfig(
        domain=domain,
        output_root=output_root,
        output_dir=output_dir,
        json_enabled=args.json,
        html_enabled=args.html,
        version=VERSION,
    )

    from lib.dotenv import find_and_load_dotenv
    find_and_load_dotenv([config.output_root])

    console = Console()
    console.print(f"[bold cyan]{BANNER}[/bold cyan]")
    console.print(f"[dim]v{VERSION} by {AUTHOR} | {domain}[/dim]\n")
    configured_keys = [k for k, v in config.api_keys.items() if v]
    if configured_keys:
        console.print(f"[dim]API keys loaded: {', '.join(configured_keys)}[/dim]\n")

    modules: List[object] = []
    if args.all or args.subdomains:
        modules.append(SubdomainModule(domain, api_keys=config.api_keys))
    if args.all or args.hosts:
        modules.append(HostsModule(domain, api_keys=config.api_keys))
    if args.all or args.urls:
        modules.append(UrlsModule(domain, api_keys=config.api_keys))
    if args.all or args.whois:
        modules.append(WhoIsModule(domain))

    run_report = args.all or args.report

    app = ReconForgeApp(config, console)
    try:
        return app.run(modules, run_report)
    except Exception as exc:
        app.logger.exception("Unhandled error")
        console.print(f"[bold red]Fatal error:[/bold red] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
