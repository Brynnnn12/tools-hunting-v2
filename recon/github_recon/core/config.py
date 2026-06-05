from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


from lib.dotenv import find_and_load_dotenv  # noqa: F401


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
