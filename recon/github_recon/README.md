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
# From root project:
./install.sh
source .venv/bin/activate
```

## Usage

```bash
export GITHUB_TOKEN=ghp_xxxxx  # Linux/macOS
set GITHUB_TOKEN=ghp_xxxxx     # Windows CMD

python github_recon.py -d example.com
python github_recon.py -d example.com --json
python github_recon.py -f domains.txt --json
python github_recon.py --version
```

**Without `GITHUB_TOKEN`:** limited to 60 requests/hour, repo + commit search only.
**With `GITHUB_TOKEN`:** 5000 requests/hour, enables code + issue search.

## Output

```
output/example.com/
  repos.txt        — repositories mentioning the domain
  commits.txt      — commits mentioning the domain
  code.txt         — code snippets (requires GITHUB_TOKEN)
  issues.txt       — issues mentioning the domain (requires GITHUB_TOKEN)
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
