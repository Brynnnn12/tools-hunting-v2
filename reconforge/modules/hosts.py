from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Set

import dns.exception
import dns.resolver

from core.utils import run_tool, which

HOST_WORDLIST = [
    "www", "mail", "ftp", "admin", "api", "blog", "dev", "test", "staging",
    "app", "portal", "webmail", "smtp", "pop3", "imap", "vpn", "remote",
    "git", "jenkins", "jira", "wiki", "cdn", "static", "assets", "docs",
    "help", "support", "forum", "news", "shop", "store", "m", "mobile",
    "web", "proxy", "secure", "login", "auth", "sso", "track", "stats",
    "ns1", "ns2", "mx1", "mx2", "server", "sql", "db", "search",
    "backup", "beta", "demo", "stage", "prod", "images", "video",
    "upload", "data", "feeds", "rss", "stream", "live", "tv",
    "panel", "cpanel", "direct", "exchange",
]

DNS_TIMEOUT = 5.0
MAX_WORKERS = 30


class HostsModule:
    name = "hosts"

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def run(self) -> List[str]:
        results: Set[str] = set()

        hostnames = [self.domain] + [f"{p}.{self.domain}" for p in HOST_WORDLIST]

        results.update(self._resolve_dns(hostnames))

        try:
            results.update(self._run_dnsx())
        except Exception:
            pass

        return sorted(results)

    def _resolve_dns(self, hostnames: List[str]) -> Set[str]:
        resolver = dns.resolver.Resolver()
        resolver.timeout = DNS_TIMEOUT
        resolver.lifetime = DNS_TIMEOUT

        results: Set[str] = set()

        def resolve(hostname: str) -> Optional[str]:
            try:
                answers = resolver.resolve(hostname, "A")
                ips = [str(r) for r in answers]
                return f"{hostname} {' '.join(ips)}"
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(resolve, h): h for h in hostnames}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.add(result)

        return results

    def _run_dnsx(self) -> Set[str]:
        if not which("dnsx"):
            return set()
        hostnames = [self.domain] + [f"{p}.{self.domain}" for p in HOST_WORDLIST[:20]]
        input_data = "\n".join(hostnames)
        try:
            import subprocess
            result = subprocess.run(
                ["dnsx", "-a", "-silent"],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if not result.stdout.strip():
                return set()
            lines: Set[str] = set()
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    lines.add(f"{parts[0]} {' '.join(parts[1:])}")
            return lines
        except Exception:
            return set()
