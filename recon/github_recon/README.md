# GitHubRecon

Search GitHub for leaked secrets, credentials, and sensitive information related to a domain.

**Author: [brynnnn12](https://github.com/brynnnn12) | Version: 1.0**

## Features

- Search GitHub code, repos, commits, and issues for domain mentions
- Secret pattern detection (AWS keys, GitHub/GitLab tokens, JWT, private keys, Slack tokens, API keys, etc.)
- Email extraction from commits and code
- Reports: TXT + optional JSON

## Installation

```bash
python -m venv .venv
# Linux/Mac: source .venv/bin/activate
# Windows:   .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python github_recon.py -h
python github_recon.py -d example.com
python github_recon.py -d example.com --json
python github_recon.py -d example.com --token ghp_xxxxx --json
python github_recon.py -f domains.txt --token ghp_xxxxx
python github_recon.py --version
```

Without `--token`: limited to 60 requests/hour, repo + commit search only.
With `--token`: 5000 requests/hour, enables code + issue search.

## Output

```
output/example.com/
  repos.txt        — repositories mentioning the domain
  commits.txt      — commits mentioning the domain
  code.txt         — code snippets (requires --token)
  issues.txt       — issues mentioning the domain (requires --token)
  emails.txt       — extracted email addresses
  secrets.txt      — detected secret patterns
  report.json      — summary (requires --json)
```

## Project Structure

```
github_recon/
  github_recon.py  — CLI entrypoint
  core/            — config, logger, utils
  modules/         — searcher, scanner, reporter
  output/          — per-target results
```
