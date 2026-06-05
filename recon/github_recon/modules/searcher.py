from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import requests


@dataclass
class SearchResult:
    code: List[dict] = field(default_factory=list)
    repos: List[dict] = field(default_factory=list)
    commits: List[dict] = field(default_factory=list)
    issues: List[dict] = field(default_factory=list)


ProgressFn = Callable[[str], None]


class Searcher:
    BASE = "https://api.github.com"
    MAX_PAGES = 10

    def __init__(
        self,
        token: str,
        user_agent: str,
        logger,
        sleep_on_limit: float = 60.0,
        max_results: int = 500,
        progress: Optional[ProgressFn] = None,
    ) -> None:
        self.token = token
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        self.logger = logger
        self.sleep_on_limit = sleep_on_limit
        self.max_results = max_results
        self.has_code_access = bool(token)
        self.progress = progress

    def _log(self, msg: str) -> None:
        if self.progress:
            self.progress(msg)
        self.logger.info(msg)

    def _get(self, path: str, params: dict) -> Optional[dict]:
        url = f"{self.BASE}{path}"

        def _json(resp):
            try:
                return resp.json()
            except (json.JSONDecodeError, ValueError):
                return {}

        for attempt in range(2):
            try:
                resp = requests.get(url, headers=self.headers, params=params, timeout=15)
                if resp.status_code == 401:
                    msg = _json(resp).get("message", "")
                    if "requires" in msg.lower():
                        self._log(f"  ~ Auth required for {path} — skipping (set GITHUB_TOKEN)")
                        return None
                    self._log(f"  ~ 401: {msg}")
                    return None
                if resp.status_code == 403:
                    body = resp.text.lower()
                    if "rate limit" in body:
                        msg = f"  ~ Rate limited — waiting {self.sleep_on_limit:.0f}s"
                        self._log(msg)
                        time.sleep(self.sleep_on_limit)
                        continue
                    if not self.token and ("code search" in body or "must have" in body):
                        self._log("  ~ Code search requires authentication (set GITHUB_TOKEN)")
                        self.has_code_access = False
                        return None
                    msg = _json(resp).get("message", "")
                    self._log(f"  ~ 403: {msg}")
                    return None
                if resp.status_code == 404:
                    return None
                if resp.status_code == 422:
                    msg = _json(resp).get("message", "")
                    self._log(f"  ~ 422: {msg}")
                    return None
                resp.raise_for_status()
                return _json(resp)
            except requests.RequestException as exc:
                self._log(f"  ~ API error: {exc}")
                return None
        return None

    def _paginate(self, path: str, params: dict, label: str = "") -> List[dict]:
        items: List[dict] = []
        page = 1
        per_page = min(100, self.max_results) if self.max_results else 100

        while len(items) < self.max_results and page <= self.MAX_PAGES:
            params["page"] = page
            params["per_page"] = per_page
            data = self._get(path, params)
            if not data:
                break
            results = data.get("items", data) if "items" in data else data
            if not results or (isinstance(results, list) and len(results) == 0):
                break
            items.extend(results)
            if isinstance(results, list) and len(results) < per_page:
                break
            page += 1

        final = items[:self.max_results]
        if label:
            self._log(f"    -> {len(final)} {label}")
        return final

    def search_code(self, query: str) -> List[dict]:
        if not self.has_code_access:
            return []
        self._log(f"  [code] {query}")
        return self._paginate("/search/code", {"q": query}, "code results")

    def search_repos(self, query: str) -> List[dict]:
        self._log(f"  [repos] {query}")
        return self._paginate("/search/repositories", {"q": query}, "repos")

    def search_commits(self, query: str) -> List[dict]:
        self._log(f"  [commits] {query}")
        return self._paginate("/search/commits", {"q": query}, "commits")

    def search_issues(self, query: str) -> List[dict]:
        if not self.token:
            return []
        self._log(f"  [issues] {query}")
        return self._paginate("/search/issues", {"q": query}, "issues")

    def search_all(self, queries: List[str]) -> SearchResult:
        result = SearchResult()
        total = sum(1 for _ in queries)  # code
        total += min(2, len(queries)) * 2  # repos + commits
        if self.token:
            total += min(2, len(queries))  # issues
        done = 0

        for q in queries:
            done += 1
            items = self.search_code(q)
            result.code.extend(items)

        for q in queries[:2]:
            done += 1
            items = self.search_repos(q)
            result.repos.extend(items)

        for q in queries[:2]:
            done += 1
            items = self.search_commits(q)
            result.commits.extend(items)

        if self.token:
            for q in queries[:2]:
                done += 1
                items = self.search_issues(q)
                result.issues.extend(items)

        return result
