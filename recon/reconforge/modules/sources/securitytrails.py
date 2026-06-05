from __future__ import annotations

import json
import urllib.request
from typing import Set


def securitytrails_subdomains(domain: str, api_key: str) -> Set[str]:
    if not api_key:
        return set()
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "APIKEY": api_key,
    })
    subdomains: Set[str] = set()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for prefix in data.get("subdomains", []):
            subdomains.add(f"{prefix}.{domain}")
    except Exception:
        pass
    return subdomains
