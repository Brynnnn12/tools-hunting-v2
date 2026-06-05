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
    reports_dir: Path = Path("reports")
    output_dir: Path = Path("output")
    logs_dir: Path = Path("logs")
    log_file: Path = Path("logs/reporthub.log")

    def __post_init__(self) -> None:
        find_and_load_dotenv()
        if _env("REPORTHUB_REPORTS_DIR", ""):
            self.reports_dir = Path(_env("REPORTHUB_REPORTS_DIR", ""))
        if _env("REPORTHUB_OUTPUT_DIR", ""):
            self.output_dir = Path(_env("REPORTHUB_OUTPUT_DIR", ""))
