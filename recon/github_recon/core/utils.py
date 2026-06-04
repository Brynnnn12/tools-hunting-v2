from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, List

from datetime import datetime, timezone


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [
        line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def now_timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def normalize_domain(domain: str) -> str:
    return domain.strip().lower().lstrip("*.")
