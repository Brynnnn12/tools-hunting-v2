from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

AUTHOR = "brynnnn12"
VERSION = "1.0"

BASE = Path(__file__).resolve().parent
TOOLS = {
    "reconforge":  BASE.parent.parent / "recon" / "reconforge" / "recon.py",
    "github_recon": BASE.parent.parent / "recon" / "github_recon" / "github_recon.py",
    "jshunter":    BASE.parent.parent / "recon" / "jshunter" / "jshunter.py",
    "asm":         BASE.parent.parent / "recon" / "attacksurfacemapper" / "asm.py",
    "scanforge":   BASE.parent.parent / "scan" / "scanforge" / "scanforge.py",
    "reporthub":   BASE.parent.parent / "report" / "reporthub" / "reporthub.py",
    "pipeline":    BASE.parent.parent / "pipeline.py",
}

BANNER = f"""
  _____                  _                 _____
 | ____|_ __   ___  __ _| |__   ___  ___  |  ___|__  _ __ _ __ _   _
 |  _| | '_ \\ / _ \\/ _` | '_ \\ / _ \\/ _ \\ | |_ / _ \\| '__| '__| | | |
 | |___| | | |  __/ (_| | | | |  __/  __/ |  _| (_) | |  | |  | |_| |
 |_____|_| |_|\\___|\\__, |_| |_|\\___|\\___| |_|  \\___/|_|  |_|   \\__, |
                    |___/                                        |___/

  EngageForge v{VERSION}  \u2014  {AUTHOR}
  Pentest engagement folder structure generator
"""

DEFAULT_STRUCTURE: List[Tuple[str, str]] = [
    ("recon", "Data collection & enumeration results"),
    ("scans", "Scan results (nuclei, nmap, etc.)"),
    ("screenshots", "Asset screenshots & evidence"),
    ("exploits", "PoC (Proof of Concept) & payloads"),
]

NOTES_TEMPLATE = """# {target} \u2014 Investigation Notes

**Target:** {target}
**Created:** {date}
**Author:** {author}

## Scope

## Attack Surface

## Findings

### [F-001] Title

**Severity:**
**Status:** Open
**Description:**
**Evidence:**
**Remediation:**

## Vulnerability Flow

```
[Entry Point] -> [Exploit] -> [Impact]
```

## Remediation Summary

"""

ENV_TEMPLATE = """# EngageForge \u2014 Engagement Metadata
TARGET={target}
CREATED={date}
AUTHOR={author}
RECON_DONE=false
JSHUNTER_DONE=false
ASM_DONE=false
SCANFORGE_DONE=false
REPORTHUB_DONE=false
"""


def create_structure(base: Path, targets: List[str], no_notes: bool = False) -> Dict[str, List[str]]:
    created: Dict[str, List[str]] = {"dirs": [], "files": []}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for target in targets:
        target_dir = base / target
        for subdir, _ in DEFAULT_STRUCTURE:
            path = target_dir / subdir
            try:
                path.mkdir(parents=True, exist_ok=True)
                created["dirs"].append(str(path))
            except (OSError, PermissionError) as exc:
                logging.warning("Failed to create %s: %s", path, exc)
        env_file = target_dir / ".env"
        try:
            if not env_file.exists():
                env_file.write_text(ENV_TEMPLATE.format(target=target, date=now, author=AUTHOR), encoding="utf-8")
                created["files"].append(str(env_file))
        except (OSError, PermissionError) as exc:
            logging.warning("Failed to write %s: %s", env_file, exc)
        if not no_notes:
            notes = target_dir / "notes.md"
            try:
                if not notes.exists():
                    notes.write_text(NOTES_TEMPLATE.format(target=target, date=now, author=AUTHOR), encoding="utf-8")
                    created["files"].append(str(notes))
            except (OSError, PermissionError) as exc:
                logging.warning("Failed to write %s: %s", notes, exc)
    return created


def print_tree(base: Path, targets: List[str]) -> None:
    for i, target in enumerate(targets):
        prefix = "\u2514\u2500\u2500 " if i == len(targets) - 1 else "\u251c\u2500\u2500 "
        print(f"{prefix}{target}/")
        target_dir = base / target
        items = sorted(target_dir.iterdir())
        for j, item in enumerate(items):
            item_prefix = "    \u2514\u2500\u2500 " if j == len(items) - 1 else "    \u251c\u2500\u2500 "
            if item.is_dir():
                print(f"{item_prefix}{item.name}/")
            else:
                size = item.stat().st_size
                print(f"{item_prefix}{item.name}  ({size} bytes)")


def run_tool(name: str, args: List[str]) -> int:
    path = TOOLS.get(name)
    if not path or not path.exists():
        print(f"  [!] {name} not found at {path}")
        return 1
    sys.stdout.flush()
    print(f"\n  \u2500\u2500 {name} \u2500\u2500\n")
    sys.stdout.flush()
    try:
        result = subprocess.run(
            [sys.executable, str(path)] + args,
            cwd=str(path.parent),
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print(f"  [!] Python executable not found")
        return 1
    return result.returncode


def mark_env(target_dir: Path, key: str, value: str = "true") -> None:
    env_path = target_dir / ".env"
    if not env_path.exists():
        return
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
        new_lines: List[str] = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
            else:
                new_lines.append(line)
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except (OSError, PermissionError) as exc:
        logging.warning("Failed to update %s: %s", env_path, exc)


def main() -> int:
    try:
        parser = argparse.ArgumentParser(
            prog="engageforge.py",
            description="Generate pentest engagement folder structure",
            epilog=(
                "Examples:\n"
                "  python engageforge.py -t example.com\n"
                "  python engageforge.py -t example.com --pipeline\n"
                "  python engageforge.py -t example.com --recon\n"
                "  python engageforge.py -t target1 target2 target3\n"
                "  python engageforge.py -t example.com -o ~/projects\n"
                "  python engageforge.py -t example.com --no-recon\n\n"
                "Author: brynnnn12  |  https://github.com/brynnnn12"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("-t", "--targets", action="append", nargs="+", metavar="TARGET", help="Target name(s) (e.g. example.com)")
        parser.add_argument("-o", "--output", default="engagements", help="Output directory (default: engagements)")
        parser.add_argument("--no-notes", action="store_true", help="Skip notes.md creation")
        parser.add_argument("--pipeline", action="store_true", help="Run full Pipeline (no prompts)")
        parser.add_argument("--recon", action="store_true", help="Run ReconForge only (no prompts)")
        parser.add_argument("--no-recon", action="store_true", help="Skip all post-setup actions (no prompts)")
        parser.add_argument("--version", action="version", version=f"EngageForge v{VERSION} \u2014 {AUTHOR}")
        args = parser.parse_args()

        if args.targets:
            targets = [t for sublist in args.targets for t in sublist]
        else:
            raw = input("  Target name: ").strip()
            if not raw:
                print("  [!] Target cannot be empty")
                return 1
            targets = [raw]

        base = Path(args.output).resolve()
        base.mkdir(parents=True, exist_ok=True)

        print(BANNER)
        print(f"  Output: {base}")
        print(f"  Target: {targets[0]}\n")

        result = create_structure(base, targets, no_notes=args.no_notes)
        print(f"  Created {len(result['dirs'])} directories, {len(result['files'])} files\n")
        print_tree(base, targets)
        print()
        print("  \u2500\u2500 Structure created \u2500\u2500\n")

        target = targets[0]
        target_dir = base / target

        if args.pipeline:
            if TOOLS["pipeline"].exists():
                run_tool("pipeline", ["-d", target])
                for key in ["RECON_DONE", "GITHUB_DONE", "JSHUNTER_DONE", "ASM_DONE", "SCANFORGE_DONE", "REPORTHUB_DONE"]:
                    mark_env(target_dir, key)
            else:
                print("  [!] pipeline.py not found")
            return 0

        if args.recon:
            run_tool("reconforge", ["-d", target, "--all", "--json"])
            mark_env(target_dir, "RECON_DONE")
            return 0

        if args.no_recon:
            return 0

        rf_output = TOOLS["reconforge"].parent / "output" / target

        steps = [
            ("ReconForge",  "reconforge",  ["-d", target, "--all", "--json"]),
            ("GitHubRecon", "github_recon", ["-d", target, "--json"]),
            ("JSHunter",    "jshunter",    ["-u", None, "--json"]),
            ("ASM",         "asm",         ["-i", str(rf_output), "--all"]),
            ("ScanForge",   "scanforge",   ["--yes", "--nuclei-category", "all", "-i", str(rf_output)]),
            ("ReportHub",   "reporthub",   ["-i", str(rf_output), "--all"]),
        ]

        env_keys = {
            "ReconForge": "RECON_DONE",
            "GitHubRecon": "GITHUB_DONE",
            "JSHunter": "JSHUNTER_DONE",
            "ASM": "ASM_DONE",
            "ScanForge": "SCANFORGE_DONE",
            "ReportHub": "REPORTHUB_DONE",
        }

        for label, name, tool_args in steps:
            answer = input(f"  Run {label}? [Y/n]: ").strip().lower()
            if answer in ("", "y", "yes"):
                if label == "JSHunter":
                    js_url = input("  JS file URL (enter to skip): ").strip()
                    if js_url:
                        run_tool(name, ["-u", js_url, "--json"])
                        mark_env(target_dir, "JSHUNTER_DONE")
                    else:
                        print("  [!] JSHunter skipped\n")
                    continue
                run_tool(name, tool_args)
                mark_env(target_dir, env_keys.get(label, f"{name.upper()}_DONE"))

        print()
        print("  \u2500\u2500 Done \u2500\u2500")
        print(f"  .env: {target_dir / '.env'}")
        return 0
    except (KeyboardInterrupt, EOFError):
        print("\n  [!] Interrupted")
        return 130
    except Exception as exc:
        logging.exception("EngageForge failed")
        print(f"\n  [red]Error:[/red] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
