# ReconForge — Agent Guide

## Quick start

```bash
# setup
python -m venv .venv; source .venv/bin/activate; pip install -r requirements.txt

# run
python recon.py -d example.com --all --json
python recon.py -d example.com --subdomains --whois
```

## CLI flags

All commands need `-d/--domain`. See `python recon.py -h` for full options. `--all` runs all modules + report. `--json` exports JSON, `--html` exports HTML report.

## Project layout

```
reconforge/
  recon.py        — entrypoint (argparse CLI, app runner)
  core/            — config, logger, utilities (stdlib-only helpers)
  modules/         — subdomains, hosts, urls, whois, reports
  output/          — per-domain output (gitignored)
  reports/         — gitignored
```

## Architecture

Modules produce real OSINT data using public APIs, DNS resolution, and external tools. Modules implement a `.run() -> List[str]` interface with a `name` class attribute. ReportModule receives `results` dict.

| Module | Method |
|---|---|
| subdomains | crt.sh API + DNS A-record brute force (~100 wordlist) + Sublist3r + Subfinder + Assetfinder + Amass (passive) |
| hosts | DNS A-record resolution (~60 hostnames) + dnsx |
| urls | HTTP GET probe (requests) + httpx + gau + waybackurls + katana (capped at 300 URLs) |
| whois | python-whois library with system `whois` fallback |
| report | Aggregates into TXT / JSON / HTML |

All modules use `ThreadPoolExecutor` (20–30 workers) for concurrent lookups. DNS timeout is 3s.

## External tools (optional, pre-installed on Kali)

| Tool | Used by | Install on Kali |
|---|---|---|
| sublist3r | subdomains | `pip install sublist3r` |
| subfinder | subdomains | `sudo apt install subfinder` |
| assetfinder | subdomains | `sudo apt install assetfinder` |
| amass | subdomains | `sudo apt install amass` |
| dnsx | hosts | `sudo apt install dnsx` |
| httpx | urls | `sudo apt install httpx` |
| gau | urls | `sudo apt install gau` |
| waybackurls | urls | `sudo apt install waybackurls` |
| katana | urls | `sudo apt install katana` |

All tools are optional — modules gracefully skip missing tools without error.

## Important constraints

- Python 3.12+ required. Dependencies: `rich>=13.7.1`, `dnspython>=2.6.0`, `requests>=2.31.0`, `python-whois>=0.9.0`.
- No test framework, no lint config, no CI, no type checker configured.
- No setup.py or pyproject.toml — project is run directly via `recon.py`.
- Output directory: `output/{domain}/`.
- `.venv/`, `__pycache__/`, `output/`, `reports/` are gitignored.
- `.github/copilot-instructions.md` is a stale project checklist, ignore it.
- Always run from `reconforge/` as working directory (recon.py uses relative paths).
- Requires internet access (crt.sh API, DNS, HTTP probing, whois).
- Author: [brynnnn12](https://github.com/brynnnn12) | Version: 0.2.0