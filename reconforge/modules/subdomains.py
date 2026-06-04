from __future__ import annotations

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Set

import dns.exception
import dns.resolver

from core.utils import run_tool, which

SUBDOMAIN_WORDLIST = [
    "www", "mail", "ftp", "admin", "api", "blog", "dev", "test", "staging",
    "app", "portal", "webmail", "smtp", "pop3", "imap", "vpn", "remote",
    "git", "jenkins", "jira", "wiki", "confluence", "status", "cdn",
    "static", "assets", "img", "css", "js", "download", "files", "media",
    "docs", "help", "support", "community", "forum", "news", "shop",
    "store", "m", "mobile", "touch", "calendar", "chat", "meet",
    "web", "proxy", "secure", "login", "auth", "register", "sso",
    "redirect", "track", "tracker", "analytics", "stats", "monitor",
    "ns1", "ns2", "ns3", "ns4", "mx1", "mx2", "dns1", "dns2",
    "server", "sql", "db", "database", "redis", "es", "elastic",
    "search", "solr", "kibana", "grafana", "prometheus", "alert",
    "backup", "beta", "demo", "sandbox", "stage", "preprod",
    "production", "prod", "release", "deploy", "ci", "cd",
    "images", "video", "upload", "data", "feeds", "rss", "xml",
    "api-v1", "v1", "v2", "api-v2", "graphql", "rest", "soap",
    "ws", "wss", "stream", "live", "tv", "radio", "player",
    "config", "settings", "panel", "manage", "administrator",
    "cpanel", "whm", "plesk", "direct", "owa", "exchange",
]

CRTSH_URL = "https://crt.sh/?q=%25.{domain}&output=json"
DNS_TIMEOUT = 3.0
MAX_WORKERS = 30


class SubdomainModule:
    name = "subdomains"

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def run(self) -> List[str]:
        results: Set[str] = set()

        try:
            results.update(self._from_crtsh())
        except Exception:
            pass

        results.update(self._dns_bruteforce())

        try:
            results.update(self._run_sublist3r())
        except Exception:
            pass

        try:
            results.update(self._run_subfinder())
        except Exception:
            pass

        try:
            results.update(self._run_assetfinder())
        except Exception:
            pass

        try:
            results.update(self._run_amass())
        except Exception:
            pass

        return sorted(results)

    def _from_crtsh(self) -> Set[str]:
        url = CRTSH_URL.format(domain=self.domain)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        subdomains: Set[str] = set()
        suffix = "." + self.domain
        for entry in data:
            names = entry.get("name_value", "")
            for name in names.split("\n"):
                name = name.strip().lower()
                if name == self.domain or name.endswith(suffix):
                    subdomains.add(name)
        return subdomains

    def _dns_bruteforce(self) -> Set[str]:
        resolver = dns.resolver.Resolver()
        resolver.timeout = DNS_TIMEOUT
        resolver.lifetime = DNS_TIMEOUT

        found: Set[str] = set()

        def check(prefix: str) -> Optional[str]:
            hostname = f"{prefix}.{self.domain}"
            try:
                resolver.resolve(hostname, "A")
                return hostname
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(check, p): p for p in SUBDOMAIN_WORDLIST}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    found.add(result)

        return found

    def _run_sublist3r(self) -> Set[str]:
        try:
            from sublist3r import sublist3r as s3r
            subs = s3r(self.domain, threads=10, silent=True, enable_bruteforce=False)
            return set(s.strip().lower() for s in subs if s.strip())
        except ImportError:
            return set()

    def _run_subfinder(self) -> Set[str]:
        if not which("subfinder"):
            return set()
        output = run_tool(["subfinder", "-d", self.domain, "-silent"])
        if not output:
            return set()
        return set(
            line.strip().lower()
            for line in output.splitlines()
            if line.strip() and not line.startswith("[")
        )

    def _run_assetfinder(self) -> Set[str]:
        if not which("assetfinder"):
            return set()
        output = run_tool(["assetfinder", "--subs-only", self.domain])
        if not output:
            return set()
        return set(line.strip().lower() for line in output.splitlines() if line.strip())

    def _run_amass(self) -> Set[str]:
        if not which("amass"):
            return set()
        output = run_tool(["amass", "enum", "-passive", "-d", self.domain, "-norecursive"])
        if not output:
            return set()
        return set(line.strip().lower() for line in output.splitlines() if line.strip())
