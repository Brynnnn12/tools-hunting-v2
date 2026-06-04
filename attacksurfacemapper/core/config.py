from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    version: str = "1.0"
    output_dir: Path = Path("output")
    reports_dir: Path = Path("reports")
    logs_dir: Path = Path("logs")
    log_file: Path = Path("logs/asm.log")
