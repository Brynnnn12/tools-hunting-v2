from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def find_and_load_dotenv() -> None:
    search_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parent.parent,
    ]
    for d in search_dirs:
        env_file = d / ".env"
        if env_file.exists():
            _load_dotenv_file(env_file)
            return


def _load_dotenv_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("\"'")
        if key and not os.environ.get(key):
            os.environ[key] = val


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
