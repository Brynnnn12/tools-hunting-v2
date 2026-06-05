from __future__ import annotations

from pathlib import Path
from typing import List, Set

from lib.utils import dedupe_preserve_order, ensure_dir, extract_domain, normalize_url, now_timestamp, read_lines, safe_filename  # noqa: F401


JS_EXTS = {".js", ".jsx", ".mjs", ".cjs"}
RECONFORGE_FILES = ["urls.txt", "urls.json", "all_urls.txt"]


def find_js_urls_from_reconforge(input_dir: Path) -> Set[str]:
    js_urls: Set[str] = set()
    for fname in RECONFORGE_FILES:
        fp = input_dir / fname
        if fp.exists():
            try:
                content = fp.read_text(encoding="utf-8", errors="ignore")
            except (OSError, PermissionError):
                continue
            for line in content.splitlines():
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
