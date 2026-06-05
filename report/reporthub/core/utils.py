import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set

from lib.utils import ensure_dir, now_timestamp, read_lines  # noqa: F401


@dataclass
class InputPaths:
    recon_dir: Path
    jshunter_dir: Path
    asm_dir: Path


def read_json(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON: {file_path}") from exc


def dedupe(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
