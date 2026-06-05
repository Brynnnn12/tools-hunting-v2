# BugBountySuite — OSINT & Recon Toolkit

All-in-one reconnaissance toolkit for bug bounty hunting, penetration testing, and attack surface mapping. Built by [brynnnn12](https://github.com/brynnnn12).

---

## Components

| Tool | Category | Location | Purpose |
|------|----------|----------|---------|
| **EngageForge** | Setup | `setup/engageforge/` | Pentest engagement folder structure generator |
| **ReconForge** | Recon | `recon/reconforge/` | Subdomain enumeration, host discovery, URL scraping, whois |
| **JSHunter** | Recon | `recon/jshunter/` | JavaScript analysis — endpoint extraction, GraphQL, storage, frameworks |
| **GitHubRecon** | Recon | `recon/github_recon/` | GitHub secret/credential leak search |
| **AttackSurfaceMapper** | Recon | `recon/attacksurfacemapper/` | Endpoint classification & attack surface graph visualization |
| **ScanForge** | Scan | `scan/scanforge/` | Automated nmap + nuclei scanning |
| **ReportHub** | Report | `report/reporthub/` | Unified HTML/JSON report & interactive dashboard |
| **Pipeline** | Orchestration | `pipeline.py` | Run all 7 tools sequentially with one command |

---

## Quick Start

```bash
# 1. One-command install (creates .venv, installs all deps)
./install.sh

# 2. Activate virtual environment
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows CMD

# 3. Run pipeline (step-by-step prompts by default)
python pipeline.py -d example.com

# 4. Or run tools individually
python recon/reconforge/recon.py -d example.com --all --json
```

---

## Installation

### Requirements

- **Python 3.10+**
- Internet connection
- (Optional) `nmap` & `nuclei` in PATH for ScanForge
- (Optional) `GITHUB_TOKEN` env var for GitHubRecon (5000 req/hr vs 60 unauthenticated)

### Installer (`./install.sh`)

| Step | Action |
|------|--------|
| 1/5 | Validate Python 3.10+ |
| 2/5 | Create `.venv` at project root (skips if exists) |
| 3/5 | Upgrade pip to latest |
| 4/5 | Install all dependencies from `requirements/*.txt` |
| 5/5 | Verify all imports succeed |

### Dependency Structure

```
requirements/
├── reconforge.txt           # rich, dnspython, requests, python-whois
├── jshunter.txt             # rich, requests, jinja2
├── github_recon.txt         # requests
├── attacksurfacemapper.txt  # rich, jinja2, networkx, matplotlib
└── reporthub.txt            # rich, jinja2, pandas, plotly, matplotlib
```

> **Note**: ScanForge & EngageForge use stdlib only — no additional dependencies.

---

## Pipeline

Run all tools in sequence with a single command. By default, prompts before each step.

```bash
python pipeline.py -d example.com          # step-by-step (recommended)
python pipeline.py -d example.com --yes     # auto-run all, no prompts
python pipeline.py -d example.com -s        # create folder structure only
python pipeline.py -d example.com -o /path  # custom output directory
```

### Output Structure

```
workspace/{domain}/
├── recon/        ← ReconForge (subdomains, hosts, urls, whois)
├── github/       ← GitHubRecon (secrets, leaks, repos)
├── jshunter/     ← JSHunter (endpoints, graphql, frameworks)
├── asm/          ← AttackSurfaceMapper (report.json, graph)
├── scan/         ← ScanForge (nmap + nuclei)
└── report/       ← ReportHub (dashboard, report)
```

### Flags

| Flag | Description |
|------|-------------|
| `-d DOMAIN` | Target domain (required) |
| `-o DIR` | Custom output directory (default: `workspace/{domain}`) |
| `-s` | Structure mode — create empty folder tree, no tools |
| `--yes` | Run all steps without prompting |
| `--skip-recon` | Skip ReconForge |
| `--skip-github` | Skip GitHubRecon |
| `--skip-jshunter` | Skip JSHunter |
| `--skip-asm` | Skip AttackSurfaceMapper |
| `--skip-scanforge` | Skip ScanForge |
| `--skip-reporthub` | Skip ReportHub |
| `--version` | Show version |

---

## Tool Reference

### EngageForge — Structure Generator

```bash
python setup/engageforge/engageforge.py -t example.com
python setup/engageforge/engageforge.py -t example.com -o ~/projects
python setup/engageforge/engageforge.py -t example.com --pipeline
```

Generates engagement folder structure with `.env` metadata and `notes.md` template.

### ReconForge — Subdomain & Host Discovery

```bash
python recon/reconforge/recon.py -d example.com --all --json --html
python recon/reconforge/recon.py -d example.com --subdomains --whois
```

**Modules**: subdomains (crt.sh, AlienVault, Shodan, SecurityTrails, LeakIX, URLScan, Sublist3r, Subfinder, Assetfinder, Amass + DNS brute-force), live hosts (dnsx, Shodan), URLs (AlienVault OTX, gau, waybackurls, katana, httpx), whois (python-whois, system whois fallback).

### JSHunter — JavaScript Analysis

```bash
python recon/jshunter/jshunter.py -u https://example.com/app.js
python recon/jshunter/jshunter.py -f js_urls.txt --json --html
python recon/jshunter/jshunter.py -i output/example.com
python recon/jshunter/jshunter.py -d ./static/js
```

**Detection**: API endpoints, GraphQL paths, WebSocket URLs, storage (localStorage/indexedDB), framework signatures, sensitive keywords, secrets.

### GitHubRecon — Secret/Leak Search

```bash
set GITHUB_TOKEN=ghp_xxx       # Windows CMD
export GITHUB_TOKEN=ghp_xxx    # Linux/macOS
python recon/github_recon/github_recon.py -d example.com --json
```

Token is read from `GITHUB_TOKEN` environment variable only — never accepted via CLI. Searches for exposed secrets, API keys, credentials, internal paths, and config files on GitHub.

### AttackSurfaceMapper — Classification & Visualization

```bash
python recon/attacksurfacemapper/asm.py -i path/to/input --all
python recon/attacksurfacemapper/asm.py -i path/to/input --html --graph
```

**Input**: `subdomains.txt`, `hosts.txt`, `urls.txt`, `endpoints.txt`, `graphql.txt`, `websockets.txt`, `frameworks.txt`, `secrets.txt`, etc.  
**Output**: Classified endpoints per category, attack surface graph (NetworkX/Matplotlib), HTML/JSON report.

### ScanForge — Automated Scanning

```bash
python scan/scanforge/scanforge.py -i output/example.com --dry-run
python scan/scanforge/scanforge.py -i output/example.com -p full
python scan/scanforge/scanforge.py -f targets.txt
```

**Profiles**: `quick` (top ports), `basic` (SYN + version), `full` (all ports), `service` (+ scripts), `vuln` (vulnerability scripts).  
Requires `nmap` and `nuclei` installed on the system.

### ReportHub — Unified Reporting

```bash
python report/reporthub/reporthub.py -i workspace/example.com --all
python report/reporthub/reporthub.py -i workspace/example.com --dashboard
```

Aggregates output from all tools and generates: interactive Plotly dashboard, HTML report, JSON export, summary statistics.

---

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GITHUB_TOKEN` | GitHub API token for GitHubRecon | Recommended (rate limit: 5000 vs 60 req/hr) |
| `SHODAN_KEY` | Shodan API key for ReconForge | Optional |
| `SECURITYTRAILS_KEY` | SecurityTrails API key | Optional |
| `ALIENVAULT_KEY` | AlienVault OTX API key | Optional |
| `LEAKIX_KEY` | LeakIX API key | Optional |
| `URLSCAN_KEY` | URLScan.io API key | Optional |

Create a `.env` file in the project root — all tools auto-load it via `lib/dotenv.py`.

---

## Directory Structure

```
BugBountySuite/
├── install.sh                # One-command installer
├── pipeline.py               # Full pipeline orchestrator
├── requirements/
│   ├── all.txt               # All dependencies combined
│   ├── reconforge.txt
│   ├── jshunter.txt
│   ├── github_recon.txt
│   ├── attacksurfacemapper.txt
│   └── reporthub.txt
├── lib/                      # Shared library
│   ├── dotenv.py             # .env file loader
│   ├── logger.py             # Console logger
│   └── utils.py              # Common utilities
├── setup/engageforge/
├── recon/
│   ├── reconforge/
│   ├── jshunter/
│   ├── github_recon/
│   └── attacksurfacemapper/
├── scan/scanforge/
└── report/reporthub/
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `./install.sh` fails | Ensure Python 3.10+ is installed and in PATH |
| Empty output | Verify the target is valid and in-scope |
| GitHubRecon rate limited | Set `GITHUB_TOKEN` environment variable |
| ScanForge fails | Install nmap (`sudo apt install nmap`) and nuclei |
| Module not found | Run `pip install -r requirements/all.txt` |
| Input file not found | Check path and directory read/write permissions |
| `Invalid IPv6 URL` error | Fixed — malformed URLs are now handled gracefully |

---

## License

See [LICENSE](LICENSE).

---

> **Author**: [brynnnn12](https://github.com/brynnnn12) — Use this toolkit only on authorized targets.
