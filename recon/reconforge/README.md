# ReconForge

Subdomain enumeration, host resolution, URL probing, and WHOIS lookup framework.

**Author: [brynnnn12](https://github.com/brynnnn12) | Version: 0.2.0**

## Features

- **Subdomain enumeration** — crt.sh, DNS brute force, Sublist3r, Subfinder, Assetfinder, Amass
- **Host resolution** — DNS A-record lookup + dnsx
- **URL probing** — requests + httpx + gau + waybackurls + katana (capped at 300 URLs)
- **Whois lookup** — python-whois with system whois fallback
- **Reports** — TXT, JSON, HTML (dark theme)
- Progress bar with rich, file logging, concurrency via ThreadPoolExecutor

## Installation

```bash
python -m venv .venv
# Linux/Mac: source .venv/bin/activate
# Windows:   .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python recon.py -h
python recon.py -d example.com --all --json --html
python recon.py -d example.com --subdomains --whois
python recon.py -d example.com --hosts
python recon.py -d example.com --urls
python recon.py -d example.com --report
python recon.py --version
```

Options: `-d/--domain` (required), `-o/--output` (default: `output`), `--all`, `--subdomains`, `--hosts`, `--urls`, `--whois`, `--report`, `--json`, `--html`.

All external tools are optional — modules skip gracefully if not installed. For best results on Kali:

```bash
sudo apt install subfinder assetfinder amass dnsx httpx gau waybackurls katana
pip install sublist3r
```

## Output

```
output/example.com/
  subdomains.txt / .json
  hosts.txt      / .json
  urls.txt       / .json
  whois.txt      / .json
  report.txt     / .json / .html
  reconforge.log
```

## Notes

- Authorized targets only. No exploitation or vulnerability scanning.
- DNS timeout: 3s. HTTP timeout: 3s. Whois timeout: 15s.
- ThreadPoolExecutor with 20–30 workers for concurrent lookups.
