from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

import lib.logger  # noqa: F401 — configures root logger

BASE = Path(__file__).resolve().parent
AUTHOR = "brynnnn12"
VERSION = "1.0"


BANNER = f"""
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                        \u2551
\u2551   BBBB   RRRR   Y   Y  N   N  N   N  N   N  N   N     \u2551
\u2551   B   B  R   R   Y Y   NN  N  NN  N  NN  N  NN  N     \u2551
\u2551   BBBB   RRRR     Y    N N N  N N N  N N N  N N N     \u2551
\u2551   B   B  R  R     Y    N  NN  N  NN  N  NN  N  NN     \u2551
\u2551   BBBB   R   R    Y    N   N  N   N  N   N  N   N     \u2551
\u2551                                                        \u2551
\u2551           ____  _       _       _                       \u2551
\u2551          |  _ \\ (_) ___| | ____| | ___                  \u2551
\u2551          | |_) | |/ __| |/ / _` |/ _ \\                 \u2551
\u2551          |  __/| | (__|   < (_| |  __/                 \u2551
\u2551          |_|   |_|\\___|_|\\_\\__,_|\\___|                 \u2551
\u2551                                                        \u2551
\u2551   Pipeline v{VERSION:<5}                               \u2551
\u2551   {AUTHOR:<47}\u2551
\u2551                                                        \u2551
\u2551   ReconForge  ->  GitHubRecon + JSHunter               \u2551
\u2551   ->  ASM  ->  ScanForge  ->  ReportHub                \u2551
\u2551                                                        \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""


def confirm(step_name: str, skip_flag: bool) -> bool:
    if skip_flag:
        return False
    answer = input(f"\n  Run {step_name}? [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")


def run(cmd: List[str], cwd: Path, desc: str) -> int:
    sys.stdout.flush()
    print(f"  \u2500\u2500 {desc} \u2500\u2500")
    sys.stdout.flush()
    logging.info("Running: %s (cwd=%s)", " ".join(str(c) for c in cmd), cwd)
    try:
        result = subprocess.run(cmd, cwd=cwd)
    except FileNotFoundError:
        print(f"  [!] {desc} failed \u2014 executable not found")
        logging.warning("%s failed \u2014 executable not found", desc)
        return 1
    if result.returncode:
        print(f"  [!] {desc} failed (exit {result.returncode})")
        logging.warning("%s failed (exit %d)", desc, result.returncode)
    return result.returncode


def main() -> int:
    try:
        parser = argparse.ArgumentParser(
            prog="pipeline.py",
            description="Full recon pipeline \u2014 ReconForge \u2192 GitHubRecon \u2192 JSHunter \u2192 ASM \u2192 ScanForge \u2192 ReportHub",
            epilog=(
                "Examples:\n"
                "  python pipeline.py -d example.com\n"
                "  python pipeline.py -d example.com -o /path/to/outputs\n"
                "  python pipeline.py -d example.com --yes\n"
                "  python pipeline.py -d example.com --skip-github\n"
                "  python pipeline.py -d example.com --skip-recon --skip-asm\n\n"
                "Output layout (default: workspace/{domain}/):\n"
                "  \u251c\u2500\u2500 recon/       \u2190 ReconForge (subdomains, hosts, urls, whois)\n"
                "  \u251c\u2500\u2500 github/      \u2190 GitHubRecon (secrets, leaks, repos)\n"
                "  \u251c\u2500\u2500 jshunter/    \u2190 JSHunter (endpoints, graphql, frameworks)\n"
                "  \u251c\u2500\u2500 asm/         \u2190 ASM (report, graph)\n"
                "  \u251c\u2500\u2500 scan/        \u2190 ScanForge (nmap + nuclei)\n"
                "  \u2514\u2500\u2500 report/      \u2190 ReportHub (dashboard, report)\n\n"
                "Author: brynnnn12  |  https://github.com/brynnnn12"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("-d", "--domain", required=True, metavar="DOMAIN", help="Target domain (e.g. example.com)")
        parser.add_argument("-o", "--output", metavar="DIR", help="Output directory (default: workspace/{domain})")
        parser.add_argument("-s", "--structure", action="store_true", help="Create folder structure only, no tools")
        parser.add_argument("--skip-recon", action="store_true", help="Skip ReconForge \u2014 subdomain/host/URL discovery")
        parser.add_argument("--skip-github", action="store_true", help="Skip GitHubRecon \u2014 GitHub leak/secret search")
        parser.add_argument("--skip-jshunter", action="store_true", help="Skip JSHunter \u2014 JS file endpoint extraction")
        parser.add_argument("--skip-asm", action="store_true", help="Skip AttackSurfaceMapper \u2014 endpoint classification & graph")
        parser.add_argument("--skip-reporthub", action="store_true", help="Skip ReportHub \u2014 unified report & dashboard")
        parser.add_argument("--skip-scanforge", action="store_true", help="Skip ScanForge \u2014 nmap + nuclei scan")
        parser.add_argument("--yes", action="store_true", help="Run all steps without prompting")
        parser.add_argument("--version", action="version", version=f"Pipeline v{VERSION} by {AUTHOR}")
        args = parser.parse_args()

        domain = args.domain
        ws = (Path(args.output).resolve() / domain) if args.output else BASE / "workspace" / domain
        ws_recon = ws / "recon"
        ws_github = ws / "github"
        ws_jsh = ws / "jshunter"
        ws_asm = ws / "asm"
        ws_scan = ws / "scan"
        ws_report = ws / "report"

        ws.mkdir(parents=True, exist_ok=True)
        ws_recon.mkdir(parents=True, exist_ok=True)
        ws_github.mkdir(parents=True, exist_ok=True)
        ws_jsh.mkdir(parents=True, exist_ok=True)
        ws_asm.mkdir(parents=True, exist_ok=True)
        ws_scan.mkdir(parents=True, exist_ok=True)
        ws_report.mkdir(parents=True, exist_ok=True)

        print(BANNER)
        print(f"  Domain: {domain}")
        print(f"  Workspace: {ws}")
        print(f"  Mode: step-by-step (use --yes to auto-run all, Ctrl+C to abort)")
        if args.structure:
            print(f"  Mode: structure only (no tools)")
        print()
        sys.stdout.flush()

        if args.structure:
            print(f"  \u2500\u2500 Structure created \u2500\u2500")
            print(f"    {ws_recon}")
            print(f"    {ws_github}")
            print(f"    {ws_jsh}")
            print(f"    {ws_asm}")
            print(f"    {ws_scan}")
            print(f"    {ws_report}")
            return 0

        PY = [sys.executable]

        # ReconForge always appends domain to its output path
        rf_out = ws / domain

        def ask(name: str, skip: bool) -> bool:
            if args.yes:
                return not skip
            return confirm(name, skip)

        # Step 1: ReconForge
        if ask("ReconForge", args.skip_recon):
            ret = run(
                PY + ["recon.py", "-d", domain, "-o", str(ws), "--all", "--json"],
                BASE / "recon" / "reconforge",
                "ReconForge \u2014 subdomains, hosts, URLs, whois",
            )
            if ret:
                print("  [!] ReconForge failed \u2014 subsequent steps may have no data\n")
            if rf_out.exists():
                ws_recon.mkdir(parents=True, exist_ok=True)
                for f in rf_out.iterdir():
                    (ws_recon / f.name).write_bytes(f.read_bytes())
                shutil.rmtree(rf_out, ignore_errors=True)
                print(f"    ReconForge output: {ws_recon}\n")
        else:
            print(f"  [-] Skipped ReconForge\n")

        # Step 2: GitHubRecon
        if ask("GitHubRecon", args.skip_github):
            ret = run(
                PY + ["github_recon.py", "-d", domain, "-o", str(ws_github), "--json"],
                BASE / "recon" / "github_recon",
                "GitHubRecon \u2014 leak & secret search",
            )
            if ret:
                print("  [!] GitHubRecon failed or no results\n")
        else:
            print(f"  [-] Skipped GitHubRecon\n")

        # Step 3: JSHunter
        if ask("JSHunter", args.skip_jshunter or not ws_recon.exists()):
            if ws_recon.exists():
                ret = run(
                    PY + ["jshunter.py", "-i", str(ws_recon), "-o", str(ws_jsh), "--json"],
                    BASE / "recon" / "jshunter",
                    "JSHunter \u2014 JS endpoint extraction from ReconForge",
                )
                if ret:
                    print("  [!] JSHunter failed or no JS URLs found\n")
            else:
                print("  [-] No ReconForge data \u2014 skipping JSHunter\n")
        else:
            print(f"  [-] Skipped JSHunter\n")

        # Step 4: ASM
        if ask("AttackSurfaceMapper", args.skip_asm):
            print("  \u2500\u2500 Preparing ASM input \u2500\u2500")

            jsh_src = ws_jsh
            if jsh_src.exists():
                subdirs = [d for d in jsh_src.iterdir() if d.is_dir()]
                jsh_src = subdirs[0] if subdirs else jsh_src

            copied = 0
            mappings = [
                (ws_recon / "subdomains.txt", ws / "subdomains.txt"),
                (ws_recon / "hosts.txt", ws / "live.txt"),
                (ws_recon / "urls.txt", ws / "all_urls.txt"),
                (jsh_src / "endpoints.txt", ws / "endpoints.txt"),
                (jsh_src / "graphql.txt", ws / "graphql.txt"),
                (jsh_src / "websockets.txt", ws / "websockets.txt"),
                (jsh_src / "storage.txt", ws / "storage.txt"),
                (jsh_src / "frameworks.txt", ws / "frameworks.txt"),
                (jsh_src / "keywords.txt", ws / "keywords.txt"),
                (jsh_src / "secrets.txt", ws / "secrets.txt"),
            ]
            for src, dst in mappings:
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
                    copied += 1
            print(f"    {copied} files prepared for ASM\n")

            ret = run(
                PY + ["asm.py", "-i", str(ws), "-o", str(ws_asm), "--all"],
                BASE / "recon" / "attacksurfacemapper",
                "AttackSurfaceMapper \u2014 classify endpoints, build graph",
            )
            if ret == 0:
                ws_asm.mkdir(parents=True, exist_ok=True)
                asm_src = BASE / "recon" / "attacksurfacemapper" / "reports"
                if asm_src.exists():
                    for f in asm_src.iterdir():
                        (ws_asm / f.name).write_bytes(f.read_bytes())
                    print(f"    ASM output: {ws_asm}\n")
        else:
            print(f"  [-] Skipped AttackSurfaceMapper\n")

        # Step 5: ScanForge
        if ask("ScanForge", args.skip_scanforge):
            if ws_recon.exists():
                ret = run(
                    PY + ["scanforge.py", "--yes", "-i", str(ws_recon), "-o", str(ws_scan), "--nuclei-category", "all"],
                    BASE / "scan" / "scanforge",
                    "ScanForge \u2014 nmap + nuclei scan",
                )
                if ret:
                    print("  [!] ScanForge failed or skipped (nmap/nuclei not installed)\n")
            else:
                print("  [-] No ReconForge data \u2014 skipping ScanForge\n")
        else:
            print(f"  [-] Skipped ScanForge\n")

        # Step 6: ReportHub
        if ask("ReportHub", args.skip_reporthub):
            ret = run(
                PY + ["reporthub.py", "-i", str(ws), "-o", str(ws_report), "--all"],
                BASE / "report" / "reporthub",
                "ReportHub \u2014 unified report & dashboard",
            )
            if ret == 0:
                print(f"    ReportHub output: {ws_report}\n")
        else:
            print(f"  [-] Skipped ReportHub\n")

        print(f"  \u2500\u2500 Done \u2500\u2500")
        print(f"  Workspace: {ws}")
        print(f"    Recon:      {ws_recon}")
        print(f"    GitHub:     {ws_github}")
        print(f"    JSHunter:   {ws_jsh}")
        print(f"    ASM:        {ws_asm}")
        print(f"    Scan:       {ws_scan}")
        print(f"    ReportHub:  {ws_report}")
        return 0
    except (KeyboardInterrupt, EOFError):
        print("\n  [!] Interrupted")
        return 130
    except Exception as exc:
        logging.exception("Pipeline failed")
        print(f"\n  [red]Error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
