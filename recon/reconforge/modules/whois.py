from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import List


class WhoIsModule:
    name = "whois"

    def __init__(self, domain: str) -> None:
        self.domain = domain

    def run(self) -> List[str]:
        try:
            return self._run_python_whois()
        except Exception:
            try:
                return self._run_system_whois()
            except Exception:
                return ["[!] Whois not available (install python-whois or system whois)"]

    def _run_python_whois(self) -> List[str]:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self._fetch_whois)
            w = future.result(timeout=15)
        lines: List[str] = []
        for key in [
            "domain_name", "registrar", "whois_server", "referral_url",
            "creation_date", "expiration_date", "updated_date",
            "name_servers", "status", "emails",
            "org", "name", "address", "city", "state", "zipcode", "country",
        ]:
            val = w.get(key)
            if val:
                if isinstance(val, list):
                    orig_len = len(val)
                    val = ", ".join(str(v).strip() for v in val[:5])
                    if orig_len > 5:
                        val += ", ..."
                lines.append(f"{key}: {val}")
        if not lines:
            lines.append("[!] No whois data returned")
        return lines

    def _fetch_whois(self):
        import whois
        return whois.whois(self.domain)

    def _run_system_whois(self) -> List[str]:
        import subprocess
        result = subprocess.run(
            ["whois", self.domain],
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout.strip()
        if not output:
            return ["[!] No whois data returned"]
        lines: List[str] = []
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith("%") and not line.startswith("#"):
                lines.append(line)
        return lines[:60]
