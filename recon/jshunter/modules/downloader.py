from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, Optional

import requests
from requests import exceptions as req_exc


class Downloader:
    def __init__(self, timeout: int, user_agent: str, logger) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}
        self.logger = logger

    def fetch_one(self, url: str) -> Optional[str]:
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.text
        except (
            req_exc.Timeout,
            req_exc.InvalidURL,
            req_exc.SSLError,
            req_exc.ConnectionError,
            req_exc.HTTPError,
            req_exc.RequestException,
        ) as exc:
            self.logger.error("Failed to download %s: %s", url, exc)
            return None

    def download_many(self, urls: Iterable[str], threads: int) -> Dict[str, str]:
        results: Dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_map = {executor.submit(self.fetch_one, url): url for url in urls}
            for future in as_completed(future_map):
                url = future_map[future]
                try:
                    content = future.result()
                except Exception as exc:  # pragma: no cover - safety net
                    self.logger.error("Unhandled error for %s: %s", url, exc)
                    continue

                if content:
                    results[url] = content
        return results
