from __future__ import annotations

import re
from typing import Dict, Set


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

    def extract(self, content: str) -> Dict[str, Set[str]]:
        endpoints = set(self.endpoint_re.findall(content))
        urls = set(self.url_re.findall(content))
        websockets = set(self.ws_re.findall(content))
        keywords = {match.lower() for match in self.keyword_re.findall(content)}
        storage = set(self.storage_re.findall(content))
        sourcemaps = set(self.sourcemap_re.findall(content))

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
        }
