from __future__ import annotations

import re
from typing import Dict, List, Set


CATEGORY_PATTERNS: Dict[str, str] = {
    "Authentication": r"(?i)(/login|/register|/logout|/forgot-password|/reset-password|/oauth|/auth|/sso|/signin|/signup)",
    "API": r"(?i)(/api/v\d+|/api|/rest|/v\d+/|/swagger|/openapi|/docs)",
    "GraphQL": r"(?i)(/graphql|/graphiql|/gql)",
    "Upload": r"(?i)(/upload|/avatar|/media|/file|/attachment|/images)",
    "Admin": r"(?i)(/admin|/dashboard|/manage|/backend|/administrator|/adminer|/phpmyadmin)",
    "User Management": r"(?i)(/users|/profile|/account|/settings|/password|/preferences)",
    "Downloads": r"(?i)(/download|/export|/report|/backup|/file)",
    "Monitoring": r"(?i)(/monitor|/health|/status|/metrics|/alerts|/logs|/debug|/traceroute|/ping)",
    "WebSocket": r"(?i)(wss?://|/ws|/socket|/connect|/stream)",
    "Storage": r"(?i)(amazonaws|s3\.|storage\.googleapis|blob\.core\.windows\.net|firebaseio)",
    "Config": r"(?i)(/config|/env|/settings|/configuration|/phpinfo|/info)",
    "Proxy": r"(?i)(/proxy|/gateway|/tunnel|/forward|/api/.*/proxy)",
    "Static Assets": r"(?i)(\.js\b|\.css\b|\.png\b|\.jpg\b|\.svg\b|\.woff|\.ttf|\.ico)",
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
