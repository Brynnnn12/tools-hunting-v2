from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Set
from urllib.parse import urlparse
import re


@dataclass
class InputBundle:
    subdomains: Set[str]
    live_hosts: Set[str]
    urls: Set[str]
    js_files: Set[str]
    endpoints: Set[str]
    graphql: Set[str]
    websockets: Set[str]
    storage: Set[str]
    frameworks: Set[str]
    keywords: Set[str]
    secrets: Set[str] = field(default_factory=set)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def now_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def read_lines(file_path: Path) -> List[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    lines = []
    for raw in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or "unknown"


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered
