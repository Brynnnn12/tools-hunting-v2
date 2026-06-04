from __future__ import annotations

import re
from typing import Dict, Set


FRAMEWORK_PATTERNS: Dict[str, str] = {
    "React": r"\breact\b|react\.createelement",
    "Vue": r"\bvue(?:\.js)?\b",
    "Angular": r"\bangular\b",
    "Next.js": r"next\.js|__NEXT_DATA__",
    "Nuxt": r"nuxt|__NUXT__",
    "Webpack": r"webpack",
    "Vite": r"vite",
    "jQuery": r"jquery",
    "Laravel": r"laravel|csrf-token.*laravel",
    "Django": r"django|csrftoken",
    "Rails": r"rails\.js|rails-ujs",
    "Svelte": r"svelte",
    "Alpine": r"alpine\.js",
    "GSAP": r"gsap",
    "D3": r"d3\.(min\.)?js",
    "Chart.js": r"chart\.(min\.)?js",
}


class Classifier:
    def __init__(self) -> None:
        self.compiled = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in FRAMEWORK_PATTERNS.items()}

    def detect(self, content: str) -> Set[str]:
        detected: Set[str] = set()
        for name, pattern in self.compiled.items():
            if pattern.search(content):
                detected.add(name)
        return detected
