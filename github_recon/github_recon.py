from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from core.config import Config
from core.logger import setup_logger
from core.utils import ensure_dir, normalize_domain, now_timestamp, read_lines, safe_filename
from modules.reporter import Reporter
from modules.scanner import Scanner
from modules.searcher import Searcher


AUTHOR = "brynnnn12"

BANNER = f"""
   ____ _ _   _ ____      ____                      __
  / ___(_) | | |  _ \\    |  _ \\ ___  ___ ___  _ __ / _|
 | |  _| | |_| | |_) |   | |_) / _ \\/ __/ _ \\| '__| |_
 | |_| | |  _  |  __/    |  _ <  __/ (_| (_) | |  |  _|
  \\____|_|_| |_|_|       |_| \\_\\___|\\___\\___/|_|  |_|

  GitHubRecon  v1.0  —  {AUTHOR}
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github_recon.py",
        description="GitHub Recon — search for leaked secrets, internal paths, and config files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-d", "--domain", help="Target domain")
    parser.add_argument("-f", "--file", help="File with domains/URLs (one per line)")
    parser.add_argument("-t", "--token", help="GitHub API token (increases rate limit to 5000/hr)")
    parser.add_argument("-o", "--output", default="output", help="Output directory (default: output)")
    parser.add_argument("--max-results", type=int, default=500, help="Max results per query (default: 500)")
    parser.add_argument("--json", action="store_true", help="Export JSON report")
    parser.add_argument("--version", action="version", version=f"GitHubRecon v1.0 — {AUTHOR}")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.domain and not args.file:
        parser.print_help()
        return 1

    domains: List[str] = []
    if args.domain:
        domains.append(normalize_domain(args.domain))
    if args.file:
        for line in read_lines(Path(args.file)):
            domains.append(normalize_domain(line))

    if not domains:
        print("[red]Error:[/red] No valid domains provided")
        return 1

    cfg = Config()
    if args.token:
        cfg.token = args.token
    if args.max_results:
        cfg.max_results = args.max_results

    output_root = Path(args.output).expanduser().resolve()
    ensure_dir(output_root)
    logger = setup_logger(output_root / "_github_recon.log")
    logger.info("Starting GitHubRecon for %d domain(s)", len(domains))

    print(BANNER)
    print(f"Target: {', '.join(domains)}\n")

    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}")
        logger.info("Processing domain: %s", domain)

        if not args.token:
            print(f"  [!] No API token — limited to 60 req/hr")
            print(f"      Use --token for code + issue search (5000 req/hr)")

        queries = [q.format(domain=domain) for q in cfg.search_queries]

        def progress(msg: str) -> None:
            print(f"  {msg}")

        searcher = Searcher(
            token=cfg.token,
            user_agent=cfg.user_agent,
            logger=logger,
            sleep_on_limit=cfg.sleep_on_limit,
            max_results=cfg.max_results,
            progress=progress,
        )

        results = searcher.search_all(queries)

        scanner = Scanner(domain, logger)

        secrets: List[str] = []
        for item in results.code:
            content = str(item)
            secrets.extend(scanner.scan_content(content, item.get("path", "?")))

        emails = scanner.extract_emails(results.code, "code")
        emails.update(scanner.extract_emails(results.commits, "commit"))

        reporter = Reporter(output_root, logger)
        reporter.save_results(
            target=safe_filename(domain),
            code_results=results.code,
            repo_results=results.repos,
            commit_results=results.commits,
            issue_results=results.issues,
            secrets=secrets,
            emails=emails,
            json_enabled=args.json,
        )

        parts = []
        if results.code:  parts.append(f"Code:{len(results.code)}")
        if results.repos:  parts.append(f"Repos:{len(results.repos)}")
        if results.commits:  parts.append(f"Commits:{len(results.commits)}")
        if results.issues:  parts.append(f"Issues:{len(results.issues)}")
        print(f"  Found: {' | '.join(parts) if parts else '(none)'}")
        if secrets:
            print(f"  [!] Secrets detected: {len(secrets)}")
        if emails:
            print(f"  [!] Emails found: {len(emails)}")
        print(f"  -> {output_root / safe_filename(domain)}\n")

    logger.info("GitHubRecon completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
