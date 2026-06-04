from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
from urllib.parse import urlparse
from datetime import datetime
import re


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


def normalize_url(url: str) -> str:
    return url.strip()


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or "unknown"


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def now_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered
