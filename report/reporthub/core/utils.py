import json
from pathlib import Path

from lib.utils import ensure_dir, now_timestamp, read_lines, dedupe_preserve_order as dedupe  # noqa: F401


def read_json(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON: {file_path}") from exc



