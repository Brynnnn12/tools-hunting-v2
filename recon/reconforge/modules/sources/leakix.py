from __future__ import annotations

import json
import urllib.request
from typing import Set


def leakix_subdomains(domain: str, api_key: str = "") -> Set[str]:
    url = f"https://leakix.net/api/subdomains/{domain}"
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        headers["api-key"] = api_key
    subdomains: Set[str] = set()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        suffix = "." + domain
        for entry in data if isinstance(data, list) else data.get("subdomains", []):
            if isinstance(entry, str):
                hostname = entry.lower()
            else:
                hostname = entry.get("subdomain", "").lower()
            if hostname and (hostname == domain or hostname.endswith(suffix)):
                subdomains.add(hostname)
    except Exception:
        pass
    return subdomains
