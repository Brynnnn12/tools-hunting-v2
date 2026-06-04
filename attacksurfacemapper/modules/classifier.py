from __future__ import annotations

import re
from typing import Dict, List, Set


CATEGORY_PATTERNS: Dict[str, str] = {
    "Authentication": r"(?i)(/login|/register|/logout|/forgot-password|/reset-password|/oauth|/auth)",
    "API": r"(?i)(/api/v\d+|/api|/rest)",
    "GraphQL": r"(?i)(/graphql)",
    "Upload": r"(?i)(/upload|/avatar|/media|/file)",
    "Admin": r"(?i)(/admin|/dashboard|/manage|/backend)",
    "User Management": r"(?i)(/users|/profile|/account|/settings)",
    "Downloads": r"(?i)(/download|/export|/report)",
    "Static Assets": r"(?i)(\.js\b|\.css\b|\.png\b|\.jpg\b|\.svg\b)",
}


class Classifier:
    def __init__(self) -> None:
        self.compiled = {name: re.compile(pattern) for name, pattern in CATEGORY_PATTERNS.items()}

    def classify(self, endpoints: Set[str]) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {name: [] for name in CATEGORY_PATTERNS}
        for endpoint in endpoints:
            for name, pattern in self.compiled.items():
                if pattern.search(endpoint):
                    results[name].append(endpoint)
        return results
