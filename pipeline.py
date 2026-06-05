from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

BASE = Path(__file__).resolve().parent
AUTHOR = "brynnnn12"
VERSION = "1.0"

LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║                                                        ║
║   BBBB   RRRR   Y   Y  N   N  N   N  N   N  N   N     ║
║   B   B  R   R   Y Y   NN  N  NN  N  NN  N  NN  N     ║
║   BBBB   RRRR     Y    N N N  N N N  N N N  N N N     ║
║   B   B  R  R     Y    N  NN  N  NN  N  NN  N  NN     ║
║   BBBB   R   R    Y    N   N  N   N  N   N  N   N     ║
║                                                        ║
║           ____  _       _       _                       ║
║          |  _ \\ (_) ___| | ____| | ___                  ║
║          | |_) | |/ __| |/ / _` |/ _ \\                 ║
║          |  __/| | (__|   < (_| |  __/                 ║
║          |_|   |_|\\___|_|\\_\\__,_|\\___|                 ║
║                                                        ║
║   Pipeline v{VERSION:<5}                               ║
║   {AUTHOR:<47}║
║                                                        ║
║   ReconForge  ->  GitHubRecon + JSHunter               ║
║   ->  ASM  ->  ScanForge  ->  ReportHub                ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
"""


def run(cmd: List[str], cwd: Path, desc: str) -> int:
    sys.stdout.flush()
    print(f"  \u2500\u2500 {desc} \u2500\u2500")
    sys.stdout.flush()
    logging.info("Running: %s (cwd=%s)", " ".join(str(c) for c in cmd), cwd)
    result = subprocess.run(cmd, cwd=cwd)
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
        parser.add_argument("--skip-recon", action="store_true", help="Skip ReconForge \u2014 subdomain/host/URL discovery")
        parser.add_argument("--skip-github", action="store_true", help="Skip GitHubRecon \u2014 GitHub leak/secret search")
        parser.add_argument("--skip-jshunter", action="store_true", help="Skip JSHunter \u2014 JS file endpoint extraction")
        parser.add_argument("--skip-asm", action="store_true", help="Skip AttackSurfaceMapper \u2014 endpoint classification & graph")
        parser.add_argument("--skip-reporthub", action="store_true", help="Skip ReportHub \u2014 unified report & dashboard")
        parser.add_argument("--skip-scanforge", action="store_true", help="Skip ScanForge \u2014 nmap + nuclei scan")
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
        print(BANNER)
        print(f"  Domain: {domain}")
        print(f"  Workspace: {ws}\n")

        PY = [sys.executable]

        # ReconForge always appends domain to its output path
        rf_out = ws / domain

        # Step 1: ReconForge
        if not args.skip_recon:
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

        # Step 2: GitHubRecon
        if not args.skip_github:
            ret = run(
                PY + ["github_recon.py", "-d", domain, "-o", str(ws_github), "--json"],
                BASE / "recon" / "github_recon",
                "GitHubRecon \u2014 leak & secret search",
            )
            if ret:
                print("  [!] GitHubRecon failed or no results\n")

        # Step 3: JSHunter
        if not args.skip_jshunter and ws_recon.exists():
            ret = run(
                PY + ["jshunter.py", "-i", str(ws_recon), "-o", str(ws_jsh), "--json"],
                BASE / "recon" / "jshunter",
                "JSHunter \u2014 JS endpoint extraction from ReconForge",
            )
            if ret:
                print("  [!] JSHunter failed or no JS URLs found\n")

        # Step 4: Prepare ASM input
        if not args.skip_asm:
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

        # Step 5: ScanForge
        if not args.skip_scanforge and ws_recon.exists():
            ret = run(
                PY + ["scanforge.py", "--yes", "-i", str(ws_recon), "-o", str(ws_scan), "--nuclei-category", "all"],
                BASE / "scan" / "scanforge",
                "ScanForge \u2014 nmap + nuclei scan",
            )
            if ret:
                print("  [!] ScanForge failed or skipped (nmap/nuclei not installed)\n")

        # Step 6: ReportHub
        if not args.skip_reporthub:
            ret = run(
                PY + ["reporthub.py", "-i", str(ws), "-o", str(ws_report), "--all"],
                BASE / "report" / "reporthub",
                "ReportHub \u2014 unified report & dashboard",
            )
            if ret == 0:
                print(f"    ReportHub output: {ws_report}\n")

        print(f"  \u2500\u2500 Done \u2500\u2500")
        print(f"  Workspace: {ws}")
        print(f"    Recon:      {ws_recon}")
        print(f"    GitHub:     {ws_github}")
        print(f"    JSHunter:   {ws_jsh}")
        print(f"    ASM:        {ws_asm}")
        print(f"    Scan:       {ws_scan}")
        print(f"    ReportHub:  {ws_report}")
        return 0
    except Exception as exc:
        logging.exception("Pipeline failed")
        print(f"\n  [red]Error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
