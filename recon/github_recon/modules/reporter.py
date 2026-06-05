from __future__ import annotations

from pathlib import Path
from typing import List, Set

from core.utils import ensure_dir, write_json, write_text


class Reporter:
    def __init__(self, output_dir: Path, logger) -> None:
        self.output_dir = output_dir
        self.logger = logger

    def save_results(
        self,
        target: str,
        code_results: List[dict],
        repo_results: List[dict],
        commit_results: List[dict],
        issue_results: List[dict],
        secrets: List[str],
        emails: Set[str],
        json_enabled: bool,
    ) -> None:
        target_dir = self.output_dir / target
        ensure_dir(target_dir)

        self._write_code(target_dir, code_results)
        self._write_repos(target_dir, repo_results)
        self._write_commits(target_dir, commit_results)
        self._write_issues(target_dir, issue_results)
        self._write_secrets(target_dir, secrets)
        self._write_emails(target_dir, emails)

        if json_enabled:
            self._write_json(
                target_dir, target,
                len(code_results), len(repo_results),
                len(commit_results), len(issue_results),
                len(secrets), len(emails),
            )

        self.logger.info("Reports saved to %s", target_dir)

    def _write_code(self, path: Path, items: List[dict]) -> None:
        lines: List[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            repo_obj = item.get("repository") or {}
            repo = repo_obj.get("full_name", "?") if isinstance(repo_obj, dict) else str(repo_obj)
            filepath = item.get("path", "?")
            html_url = item.get("html_url", "")
            lines.append(f"{repo} | {filepath}")
            if html_url:
                lines.append(f"  {html_url}")
        write_text(path / "code.txt", "\n".join(lines) + ("\n" if lines else ""))

    def _write_repos(self, path: Path, items: List[dict]) -> None:
        lines: List[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("full_name", item.get("name", "?"))
            desc = item.get("description", "") or ""
            url = item.get("html_url", "")
            lines.append(f"{name}")
            if desc:
                lines.append(f"  {desc}")
            lines.append(f"  {url}")
        write_text(path / "repos.txt", "\n".join(lines) + ("\n" if lines else ""))

    def _write_commits(self, path: Path, items: List[dict]) -> None:
        lines: List[str] = []
        for item in items:
            repo_obj = item.get("repository") or {}
            repo = repo_obj.get("full_name", "?") if isinstance(repo_obj, dict) else str(repo_obj)
            commit_obj = item.get("commit") or {}
            msg = commit_obj.get("message", "?").split("\n")[0] if isinstance(commit_obj, dict) else "?"
            url = item.get("html_url", "")
            author_obj = commit_obj.get("author") or {} if isinstance(commit_obj, dict) else {}
            author = author_obj.get("name", "?") if isinstance(author_obj, dict) else "?"
            lines.append(f"{repo} | {author} | {msg}")
            lines.append(f"  {url}")
        write_text(path / "commits.txt", "\n".join(lines) + ("\n" if lines else ""))

    def _write_issues(self, path: Path, items: List[dict]) -> None:
        lines: List[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            repo = (item.get("repository_url") or "").replace("https://api.github.com/repos/", "")
            title = item.get("title", "?")
            url = item.get("html_url", "")
            state = item.get("state", "?")
            lines.append(f"[{state}] {repo} | {title}")
            lines.append(f"  {url}")
        write_text(path / "issues.txt", "\n".join(lines) + ("\n" if lines else ""))

    def _write_secrets(self, path: Path, items: List[str]) -> None:
        write_text(path / "secrets.txt", "\n".join(items) + ("\n" if items else ""))

    def _write_emails(self, path: Path, items: Set[str]) -> None:
        write_text(path / "emails.txt", "\n".join(sorted(items)) + ("\n" if items else ""))

    def _write_json(
        self, path: Path, target: str,
        total_code: int, total_repos: int,
        total_commits: int, total_issues: int,
        total_secrets: int, total_emails: int,
    ) -> None:
        write_json(path / "report.json", {
            "target": target,
            "author": "brynnnn12",
            "total_code_results": total_code,
            "total_repos": total_repos,
            "total_commits": total_commits,
            "total_issues": total_issues,
            "total_secrets": total_secrets,
            "total_emails": total_emails,
        })
