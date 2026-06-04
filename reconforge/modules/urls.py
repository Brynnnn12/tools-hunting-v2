from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Set

import requests as req

from core.utils import run_tool, which

HTTP_TIMEOUT = 3.0
MAX_WORKERS = 20
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
MAX_URLS = 300


class UrlsModule:
    name = "urls"

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def run(self) -> List[str]:
        candidates: Set[str] = set()

        candidates.add(f"https://{self.domain}/")
        candidates.add(f"http://{self.domain}/")
        for prefix in ["www", "api", "mail", "admin", "dev", "blog", "cdn", "app", "portal", "shop", "docs", "status", "support", "wiki"]:
            candidates.add(f"https://{prefix}.{self.domain}/")
            candidates.add(f"http://{prefix}.{self.domain}/")

        try:
            for url in self._run_gau():
                candidates.add(url)
                if len(candidates) >= MAX_URLS:
                    break
        except Exception:
            pass

        try:
            for url in self._run_waybackurls():
                candidates.add(url)
                if len(candidates) >= MAX_URLS:
                    break
        except Exception:
            pass

        try:
            for url in self._run_katana():
                candidates.add(url)
                if len(candidates) >= MAX_URLS:
                    break
        except Exception:
            pass

        results = self._probe(list(candidates)[:MAX_URLS])

        try:
            httpx_results = self._run_httpx(list(candidates)[:50])
            seen = set(results)
            for item in httpx_results:
                if item not in seen:
                    results.append(item)
                    seen.add(item)
        except Exception:
            pass

        return sorted(results)

    def _probe(self, urls: List[str]) -> List[str]:
        results: List[str] = []

        def probe(url: str) -> Optional[str]:
            try:
                resp = req.get(
                    url,
                    timeout=HTTP_TIMEOUT,
                    headers={"User-Agent": USER_AGENT},
                    allow_redirects=True,
                )
                return f"{url} [{resp.status_code}] ({len(resp.content)} bytes)"
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(probe, u): u for u in urls}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        return results

    def _run_gau(self) -> Set[str]:
        if not which("gau"):
            return set()
        output = run_tool(["gau", self.domain], timeout=30)
        if not output:
            return set()
        urls: Set[str] = set()
        for line in output.splitlines():
            line = line.strip()
            if line:
                urls.add(line)
        return urls

    def _run_waybackurls(self) -> Set[str]:
        if not which("waybackurls"):
            return set()
        output = run_tool(["waybackurls", self.domain], timeout=30)
        if not output:
            return set()
        urls: Set[str] = set()
        for line in output.splitlines():
            line = line.strip()
            if line:
                urls.add(line)
        return urls

    def _run_katana(self) -> Set[str]:
        if not which("katana"):
            return set()
        output = run_tool(
            ["katana", "-u", f"https://{self.domain}", "-silent", "-d", "1"],
            timeout=30,
        )
        if not output:
            return set()
        urls: Set[str] = set()
        for line in output.splitlines():
            line = line.strip()
            if line:
                urls.add(line)
        return urls

    def _run_httpx(self, candidates: List[str]) -> List[str]:
        if not which("httpx"):
            return []
        import subprocess
        try:
            result = subprocess.run(
                ["httpx", "-silent", "-status-code", "-content-length"],
                input="\n".join(candidates),
                capture_output=True, text=True,
                timeout=15,
            )
            if not result.stdout.strip():
                return []
            lines: List[str] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    parts = line.rsplit(None, 2)
                    if len(parts) == 3:
                        url, raw_code, raw_size = parts
                        code = raw_code.strip("[]")
                        size = raw_size.strip("[]B")
                        lines.append(f"{url} [{code}] ({size} bytes)")
                    else:
                        lines.append(line)
            return lines
        except Exception:
            return []
