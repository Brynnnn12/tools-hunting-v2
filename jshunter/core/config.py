from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    version: str = "1.0"
    default_threads: int = 20
    timeout: int = 15
    user_agent: str = "JSHunter/1.0"
    output_dir: Path = Path("output")
    reports_dir: Path = Path("reports")
    logs_dir: Path = Path("logs")
    log_file: Path = Path("logs/jshunter.log")
