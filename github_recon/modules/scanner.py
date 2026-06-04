from __future__ import annotations

import re
from typing import Dict, List, Set


SECRET_PATTERNS: Dict[str, str] = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws[_\-\.]?secret[_\-\.]?access[_\-\.]?key.{0,30}['\"][A-Za-z0-9+/=]{40}['\"]",
    "GitHub Token": r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,252}",
    "GitLab Token": r"glpat-[A-Za-z0-9\-_]{20,40}",
    "Slack Token": r"xox[baprs]-[0-9]{12,13}-[0-9]{12,13}-[A-Za-z0-9]{24}",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
    "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
    "JWT Token": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "Private Key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Generic Secret": r"(?i)(?:password|secret|api[_-]?key|auth[_-]?token|access[_-]?token)[\"']?\s*[:=]\s*[\"'][^\"']{8,}[\"']",
    "Connection String": r"(?i)(?:mongodb|postgresql|mysql|redis)://[^\s'\"<>]{8,}",
    "Heroku API Key": r"[hH][eE][rR][oO][kK][uU].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
    "npm Token": r"npm_[A-Za-z0-9]{36}",
    "PyPI Token": r"pypi-[A-Za-z0-9]{40,60}",
    "Discord Token": r"[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}",
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class Scanner:
    def __init__(self, domain: str, logger) -> None:
        self.domain = domain.lower()
        self.logger = logger
        self.compiled = {name: re.compile(pattern) for name, pattern in SECRET_PATTERNS.items()}

    def scan_content(self, content: str, source: str) -> List[str]:
        findings: List[str] = []
        for name, pattern in self.compiled.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                snippet = content[max(0, match.start() - 40):match.end() + 40].replace("\n", " ")
                findings.append(f"[{name}] {source}:{line_num} | ...{snippet.strip()}...")
        return findings

    def extract_emails(self, items: List[dict], source_type: str) -> Set[str]:
        emails: Set[str] = set()
        for item in items:
            if not item:
                continue
            text = str(item)
            for email in EMAIL_RE.findall(text):
                if email.lower().endswith(self.domain) or any(
                    kw in text.lower() for kw in [self.domain, "@" + self.domain]
                ):
                    emails.add(email.lower())
        return emails
