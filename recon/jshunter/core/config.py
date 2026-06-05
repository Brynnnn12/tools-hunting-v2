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
        if _env("JSHUNTER_THREADS", ""):
            self.default_threads = int(_env("JSHUNTER_THREADS", ""))
        if _env("JSHUNTER_TIMEOUT", ""):
            self.timeout = int(_env("JSHUNTER_TIMEOUT", ""))
        if _env("JSHUNTER_USER_AGENT", ""):
            self.user_agent = _env("JSHUNTER_USER_AGENT", "")
