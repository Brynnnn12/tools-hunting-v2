from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


from lib.dotenv import find_and_load_dotenv  # noqa: F401


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


@dataclass
class Config:
    version: str = "1.0"
    default_threads: int = 20
    timeout: int = 15
    user_agent: str = "JSHunter/1.0"
    output_dir: Path = Path("output")
    reports_dir: Path = Path("reports")
    logs_dir: Path = Path("logs")
    log_file: Path = Path("logs/jshunter.log")

    def __post_init__(self) -> None:
        find_and_load_dotenv()
        threads_raw = _env("JSHUNTER_THREADS", "")
        if threads_raw:
            try:
                self.default_threads = int(threads_raw)
            except ValueError:
                pass
        timeout_raw = _env("JSHUNTER_TIMEOUT", "")
        if timeout_raw:
            try:
                self.timeout = int(timeout_raw)
            except ValueError:
                pass
        if _env("JSHUNTER_USER_AGENT", ""):
            self.user_agent = _env("JSHUNTER_USER_AGENT", "")
