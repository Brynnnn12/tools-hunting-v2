from __future__ import annotations

import re
from typing import Dict, Set


SECRET_PATTERNS: Dict[str, str] = {
    "AWS Key": r"(?i)(AKIA[0-9A-Z]{16})",
    "GitHub Token": r"(?i)gh[pousr]_[A-Za-z0-9_]{36,}",
    "GitLab Token": r"(?i)glpat-[A-Za-z0-9\-_]{20,}",
    "Slack Token": r"(?i)xox[baprs]-[0-9A-Za-z\-]{10,}",
    "Google API Key": r"(?i)AIza[0-9A-Za-z\-_]{35}",
    "Stripe Key": r"(?i)sk_live_[0-9A-Za-z]{24,}",
    "JWT Token": r"eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
    "Firebase URL": r"(?i)https://[A-Za-z0-9\-_]+\.firebaseio\.com",
    "Heroku API Key": r"(?i)[hH][eE][rR][oO][kK][uU].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
    "Private Key": r"-----BEGIN\s?(RSA|DSA|EC|PGP|OPENSSH)?\s?PRIVATE KEY-----",
}


class Extractor:
    def __init__(self) -> None:
        self.url_re = re.compile(
            r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+"
        )
        self.ws_re = re.compile(
            r"wss?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+"
        )
        self.sourcemap_re = re.compile(r"sourceMappingURL=([^\s'\"\\]+)")
        self.endpoint_re = re.compile(
            r"(?i)(/api/v\d+|/api|/graphql|/auth|/login|/logout|/admin|/upload|/dashboard|/internal)"
        )
        self.keyword_re = re.compile(
            r"(?i)\b(admin|internal|private|debug|token|secret|apikey|staging|dev|test|beta)\b"
        )
        self.storage_re = re.compile(
            r"(?i)(amazonaws\.com|s3\.amazonaws\.com|storage\.googleapis\.com|blob\.core\.windows\.net)"
        )
        self.secrets_compiled = {
            name: re.compile(pattern) for name, pattern in SECRET_PATTERNS.items()
        }

    def extract(self, content: str) -> Dict[str, Set[str]]:
        endpoints = set(self.endpoint_re.findall(content))
        urls = set(self.url_re.findall(content))
        websockets = set(self.ws_re.findall(content))
        keywords = {match.lower() for match in self.keyword_re.findall(content)}
        storage = set(self.storage_re.findall(content))
        sourcemaps = set(self.sourcemap_re.findall(content))

        secrets: Set[str] = set()
        for name, pattern in self.secrets_compiled.items():
            for match in pattern.finditer(content):
                secrets.add(f"{name}: {match.group()[:80]}")

        graphql = {item for item in endpoints if item.lower().startswith("/graphql")}
        graphql.update({url for url in urls if "/graphql" in url.lower()})

        return {
            "endpoints": endpoints,
            "urls": urls,
            "graphql": graphql,
            "websockets": websockets,
            "storage": storage,
            "keywords": keywords,
            "sourcemaps": sourcemaps,
            "secrets": secrets,
        }
