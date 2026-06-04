from __future__ import annotations

import argparse
import re
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
  Unified recon: ReconForge  →  JSHunter  →  ASM  →  ReportHub
"""


def run(cmd: str, cwd: Path, desc: str) -> int:
    print(f"  ── {desc} ──")
    sys.stdout.flush()
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode:
        print(f"  [!] {desc} failed (exit {result.returncode})")
    return result.returncode


def extract_clean_urls(urls_path: Path) -> List[str]:
    if not urls_path.exists():
        return []
    clean: List[str] = []
    for line in urls_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        url = re.sub(r"\s*\[.*?\]\s*\(.*?\)\s*$", "", line).strip()
        if url and url.startswith("http"):
            clean.append(url)
    return clean


def guess_js_urls(all_urls: List[str]) -> List[str]:
    js_exts = {".js", ".jsx", ".mjs", ".cjs"}
    return [u for u in all_urls if any(u.lower().endswith(ext) for ext in js_exts)]


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="pipeline.py",
        description="Full recon pipeline — ReconForge → JSHunter → AttackSurfaceMapper → ReportHub",
        epilog=(
            "Examples:\n"
            "  python pipeline.py -d example.com\n"
            "  python pipeline.py -d example.com --skip-jshunter\n"
            "  python pipeline.py -d example.com --skip-recon --skip-asm\n\n"
            "Output layout:\n"
            "  workspace/{domain}/\n"
            "  ├── recon/       ← ReconForge (subdomains, hosts, urls, whois)\n"
            "  ├── jshunter/    ← JSHunter (endpoints, graphql, frameworks)\n"
            "  ├── asm/         ← AttackSurfaceMapper (report, graph)\n"
            "  └── report/      ← ReportHub (dashboard, report)\n\n"
            "Author: brynnnn12  |  https://github.com/brynnnn12"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-d", "--domain", required=True, metavar="DOMAIN", help="Target domain (e.g. example.com)")
    parser.add_argument("--skip-recon", action="store_true", help="Skip ReconForge — subdomain/host/URL discovery")
    parser.add_argument("--skip-jshunter", action="store_true", help="Skip JSHunter — JS file endpoint extraction")
    parser.add_argument("--skip-asm", action="store_true", help="Skip AttackSurfaceMapper — endpoint classification & graph")
    parser.add_argument("--skip-reporthub", action="store_true", help="Skip ReportHub — unified report & dashboard")
    parser.add_argument("--version", action="version", version=f"Pipeline v{VERSION} by {AUTHOR}")
    args = parser.parse_args()

    domain = args.domain
    ws = BASE / "workspace" / domain
    ws_recon = ws / "recon"
    ws_jsh = ws / "jshunter"
    ws_asm = ws / "asm"
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
            BASE / "reconforge",
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

    # ── Step 2: JSHunter ──
    if not args.skip_jshunter:
        js_urls: List[str] = []
        for txt in [ws_recon / "urls.txt", ws_recon / "recon.txt"]:
            js_urls = guess_js_urls(extract_clean_urls(txt))
            if js_urls:
                break

        if js_urls:
            js_list = ws / "_js_urls.txt"
            js_list.write_text("\n".join(js_urls) + "\n", encoding="utf-8")
            print(f"  Found {len(js_urls)} JS URLs from ReconForge output\n")
            ret = run(
                f"python jshunter.py -f \"{js_list}\" -o \"{ws_jsh}\" --json",
                BASE / "jshunter",
                f"JSHunter — JS analysis ({len(js_urls)} URLs)",
            )
            js_list.unlink(missing_ok=True)
            if ret:
                print("  [!] JSHunter failed\n")
        else:
            print("  [!] No JS URLs found in ReconForge output — skipping JSHunter")
            print("      Run JSHunter manually with -u or -f for JS file URLs\n")

    # ── Step 3: Prepare ASM input ──
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
        ]
        for src, dst in mappings:
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                copied += 1
        print(f"    {copied} files prepared for ASM\n")

        ret = run(
            f"python asm.py -i \"{ws}\" --all",
            BASE / "attacksurfacemapper",
            "AttackSurfaceMapper — classify endpoints, build graph",
        )
        if ret == 0:
            ws_asm.mkdir(parents=True, exist_ok=True)
            asm_src = BASE / "attacksurfacemapper" / "reports"
            if asm_src.exists():
                for f in asm_src.iterdir():
                    (ws_asm / f.name).write_bytes(f.read_bytes())
                print(f"    ASM output: {ws_asm}\n")

    # ── Step 4: ReportHub ──
    if not args.skip_reporthub:
        ret = run(
            f"python reporthub.py -i \"{ws}\" --all",
            BASE / "reporthub",
            "ReportHub — unified report & dashboard",
        )
        if ret == 0:
            rh_src = BASE / "reporthub" / "reports"
            if rh_src.exists():
                ws_report.mkdir(parents=True, exist_ok=True)
                for f in rh_src.iterdir():
                    (ws_report / f.name).write_bytes(f.read_bytes())
                print(f"    ReportHub output: {ws_report}\n")

    print(f"  ── Done ──")
    print(f"  Workspace: {ws}")
    print(f"    Recon:     {ws_recon}")
    print(f"    JSHunter:  {ws_jsh}")
    print(f"    ASM:       {ws_asm}")
    print(f"    ReportHub: {ws_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
