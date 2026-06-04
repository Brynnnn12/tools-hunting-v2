from __future__ import annotations

import json
import urllib.request
from typing import Set


def alienvault_passive_dns(domain: str, api_key: str = "") -> Set[str]:
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        headers["X-OTX-API-KEY"] = api_key
    subdomains: Set[str] = set()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        suffix = "." + domain
        for entry in data.get("passive_dns", []):
            hostname = entry.get("hostname", "")
            if hostname == domain or hostname.endswith(suffix):
                subdomains.add(hostname.lower())
    except Exception:
        pass
    return subdomains


def alienvault_url_list(domain: str, api_key: str = "") -> Set[str]:
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/url_list"
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        headers["X-OTX-API-KEY"] = api_key
    urls: Set[str] = set()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for entry in data.get("url_list", []):
            u = entry.get("url", "")
            if u:
                urls.add(u)
    except Exception:
        pass
    return urls
