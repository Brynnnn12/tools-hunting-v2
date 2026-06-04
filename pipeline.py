from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

BASE = Path(__file__).resolve().parent
AUTHOR = "brynnnn12"
VERSION = "1.0"


def banner() -> str:
    return f"""
  ____  _       _       _        ____  _       _       _
 |  _ \\ (_) ___| | ____| | ___  |  _ \\| | ___ | |_ ___ _ __
 | |_) | |/ __| |/ / _` |/ _ \\ | |_) | |/ _ \\| __/ _ \\ '_ \\
 |  __/| | (__|   < (_| |  __/ |  __/| | (_) | ||  __/ | | |
 |_|   |_|\\___|_|\\_\\__,_|\\___| |_|   |_|\\___/ \\__\\___|_| |_|

  Pipeline v{VERSION}  —  {AUTHOR}
  Unified recon: ReconForge  →  GitHubRecon + JSHunter  →  ASM  →  ScanForge  →  ReportHub
"""


def run(cmd: str, cwd: Path, desc: str) -> int:
    print(f"  ── {desc} ──")
    sys.stdout.flush()
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode:
        print(f"  [!] {desc} failed (exit {result.returncode})")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="pipeline.py",
        description="Full recon pipeline — ReconForge → GitHubRecon → JSHunter → ASM → ScanForge → ReportHub",
        epilog=(
            "Examples:\n"
            "  python pipeline.py -d example.com\n"
            "  python pipeline.py -d example.com --skip-github\n"
            "  python pipeline.py -d example.com --skip-recon --skip-asm\n\n"
            "Output layout:\n"
            "  workspace/{domain}/\n"
            "  ├── recon/       ← ReconForge (subdomains, hosts, urls, whois)\n"
            "  ├── github/      ← GitHubRecon (secrets, leaks, repos)\n"
            "  ├── jshunter/    ← JSHunter (endpoints, graphql, frameworks)\n"
            "  ├── asm/         ← ASM (report, graph)\n"
            "  ├── scan/        ← ScanForge (nmap + nuclei)\n"
            "  └── report/      ← ReportHub (dashboard, report)\n\n"
            "Author: brynnnn12  |  https://github.com/brynnnn12"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-d", "--domain", required=True, metavar="DOMAIN", help="Target domain (e.g. example.com)")
    parser.add_argument("--skip-recon", action="store_true", help="Skip ReconForge — subdomain/host/URL discovery")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHubRecon — GitHub leak/secret search")
    parser.add_argument("--skip-jshunter", action="store_true", help="Skip JSHunter — JS file endpoint extraction")
    parser.add_argument("--skip-asm", action="store_true", help="Skip AttackSurfaceMapper — endpoint classification & graph")
    parser.add_argument("--skip-reporthub", action="store_true", help="Skip ReportHub — unified report & dashboard")
    parser.add_argument("--skip-scanforge", action="store_true", help="Skip ScanForge — nmap + nuclei scan")
    parser.add_argument("--version", action="version", version=f"Pipeline v{VERSION} by {AUTHOR}")
    args = parser.parse_args()

    domain = args.domain
    ws = BASE / "workspace" / domain
    ws_recon = ws / "recon"
    ws_github = ws / "github"
    ws_jsh = ws / "jshunter"
    ws_asm = ws / "asm"
    ws_scan = ws / "scan"
    ws_report = ws / "report"

    ws.mkdir(parents=True, exist_ok=True)
    print(banner())
    print(f"  Domain: {domain}")
    print(f"  Workspace: {ws}\n")

    # ReconForge always appends domain to its output path
    rf_out = ws / domain  # ReconForge writes to {ws}/{domain}/

    # ── Step 1: ReconForge ──
    if not args.skip_recon:
        ret = run(
            f"python recon.py -d {domain} -o \"{ws}\" --all --json",
            BASE / "recon" / "reconforge",
            "ReconForge — subdomains, hosts, URLs, whois",
        )
        if ret:
            print("  [!] ReconForge failed — subsequent steps may have no data\n")
        # Move ReconForge output into ws/recon/
        if rf_out.exists():
            ws_recon.mkdir(parents=True, exist_ok=True)
            for f in rf_out.iterdir():
                (ws_recon / f.name).write_bytes(f.read_bytes())
            import shutil
            shutil.rmtree(rf_out, ignore_errors=True)
            print(f"    ReconForge output: {ws_recon}\n")

    # ── Step 2: GitHubRecon ──
    if not args.skip_github:
        ret = run(
            f"python github_recon.py -d {domain} -o \"{ws_github}\" --json",
            BASE / "recon" / "github_recon",
            "GitHubRecon — leak & secret search",
        )
        if ret:
            print("  [!] GitHubRecon failed or no results\n")

    # ── Step 3: JSHunter ──
    if not args.skip_jshunter and ws_recon.exists():
        ret = run(
            f"python jshunter.py -i \"{ws_recon}\" -o \"{ws_jsh}\" --json",
            BASE / "recon" / "jshunter",
            "JSHunter — JS endpoint extraction from ReconForge",
        )
        if ret:
            print("  [!] JSHunter failed or no JS URLs found\n")

    # ── Step 4: Prepare ASM input ──
    if not args.skip_asm:
        print("  ── Preparing ASM input ──")

        # Find JSHunter target subfolder (domain or "mixed")
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
            f"python asm.py -i \"{ws}\" -o \"{ws_asm}\" --all",
            BASE / "recon" / "attacksurfacemapper",
            "AttackSurfaceMapper — classify endpoints, build graph",
        )
        if ret == 0:
            ws_asm.mkdir(parents=True, exist_ok=True)
            asm_src = BASE / "recon" / "attacksurfacemapper" / "reports"
            if asm_src.exists():
                for f in asm_src.iterdir():
                    (ws_asm / f.name).write_bytes(f.read_bytes())
                print(f"    ASM output: {ws_asm}\n")

    # ── Step 5: ScanForge ──
    if not args.skip_scanforge and ws_recon.exists():
        ret = run(
            f"python scanforge.py --yes -i \"{ws_recon}\" -o \"{ws_scan}\" --nuclei-category all",
            BASE / "scan" / "scanforge",
            "ScanForge — nmap + nuclei scan",
        )
        if ret:
            print("  [!] ScanForge failed or skipped (nmap/nuclei not installed)\n")

    # ── Step 6: ReportHub ──
    if not args.skip_reporthub:           
        ret = run(
            f"python reporthub.py -i \"{ws}\" -o \"{ws_report}\" --all",
            BASE / "report" / "reporthub",
            "ReportHub — unified report & dashboard",
        )
        if ret == 0:
            print(f"    ReportHub output: {ws_report}\n")

    print(f"  ── Done ──")
    print(f"  Workspace: {ws}")
    print(f"    Recon:      {ws_recon}")
    print(f"    GitHub:     {ws_github}")
    print(f"    JSHunter:   {ws_jsh}")
    print(f"    ASM:        {ws_asm}")
    print(f"    Scan:       {ws_scan}")
    print(f"    ReportHub:  {ws_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
