from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Set
from urllib.parse import urlparse
from datetime import datetime
import re


JS_EXTS = {".js", ".jsx", ".mjs", ".cjs"}
RECONFORGE_FILES = ["urls.txt", "urls.json", "all_urls.txt"]


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


def find_js_urls_from_reconforge(input_dir: Path) -> Set[str]:
    js_urls: Set[str] = set()
    for fname in RECONFORGE_FILES:
        fp = input_dir / fname
        if fp.exists():
            for line in fp.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                url = line.split()[0] if line.startswith("http") else line
                if any(url.lower().endswith(ext) for ext in JS_EXTS):
                    js_urls.add(url)
    return js_urls


def find_js_files_local(directory: Path) -> List[Path]:
    js_files: List[Path] = []
    for ext in JS_EXTS:
        js_files.extend(directory.rglob(f"*{ext}"))
    return sorted(js_files)

