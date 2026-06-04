from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List
import json


@dataclass
class InputPaths:
    recon_dir: Path
    jshunter_dir: Path
    asm_dir: Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def now_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_lines(file_path: Path) -> List[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    lines: List[str] = []
    for raw in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def read_json(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON: {file_path}") from exc


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered
