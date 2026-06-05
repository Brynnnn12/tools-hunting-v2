from __future__ import annotations

import os
from pathlib import Path
from typing import List


def find_and_load_dotenv(search_dirs: List[Path] | None = None) -> bool:
    if search_dirs is None:
        search_dirs = [Path.cwd()]
    for d in search_dirs:
        env_file = d / ".env"
        if env_file.exists():
            _load_dotenv_file(env_file)
            return True
    return False


def _load_dotenv_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("\"'")
        if key and not os.environ.get(key):
            os.environ[key] = val
