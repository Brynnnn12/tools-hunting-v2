from __future__ import annotations

import json
import urllib.request
from typing import Set


def urlscan_subdomains(domain: str, api_key: str = "") -> Set[str]:
    url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        headers["API-Key"] = api_key
    results: Set[str] = set()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        suffix = "." + domain
        for result in data.get("results", []):
            page = result.get("page", {})
            dom = page.get("domain", "")
            if dom == domain or dom.endswith(suffix):
                results.add(dom.lower())
    except Exception:
        pass
    return results
