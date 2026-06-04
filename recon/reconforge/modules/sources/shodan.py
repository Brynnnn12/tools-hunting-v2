from __future__ import annotations

import json
import urllib.request
from typing import Dict, List, Set


def shodan_subdomains(domain: str, api_key: str) -> Set[str]:
    if not api_key:
        return set()
    url = f"https://api.shodan.io/dns/domain/{domain}?key={api_key}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        subdomains: Set[str] = set()
        for entry in data.get("data", []):
            sub = entry.get("subdomain", "")
            if sub:
                subdomains.add(f"{sub}.{domain}")
        return subdomains
    except Exception:
        return set()


def shodan_host_search(domain: str, api_key: str) -> Set[str]:
    if not api_key:
        return set()
    results: Set[str] = set()
    url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query=hostname:{domain}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for match in data.get("matches", []):
            hostname = match.get("hostnames", [])
            for h in hostname:
                if h.endswith("." + domain) or h == domain:
                    results.add(h)
            ip = match.get("ip_str")
            if ip and hostname:
                results.add(f"{hostname[0]} {ip}")
    except Exception:
        pass
    return results
