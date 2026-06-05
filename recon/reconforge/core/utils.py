from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from lib.utils import ensure_dir, normalize_domain, now_timestamp, write_json, write_text  # noqa: F401


def which(binary: str) -> Optional[str]:
    return shutil.which(binary)


def run_tool(cmd: List[str], timeout: int = 30) -> Optional[str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return None
