from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


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


@dataclass
class Config:
    token: str = ""
    per_page: int = 100
    user_agent: str = "GitHubRecon/1.0"
    output_dir: str = "output"
    sleep_on_limit: float = 60.0
    max_results: int = 500
    search_queries: List[str] = field(default_factory=lambda: [
        "{domain}",
        "\"{domain}\" password",
        "\"{domain}\" secret",
        "\"{domain}\" key",
        "\"{domain}\" config",
        "\"{domain}\" api",
        "\"{domain}\" token",
        "\"{domain}\" internal",
        "\"{domain}\" database",
        "\"{domain}\" connection",
    ])

    def __post_init__(self) -> None:
        find_and_load_dotenv()
        env_token = os.environ.get("GITHUB_TOKEN", "")
        if env_token:
            self.token = env_token
