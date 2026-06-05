# ReconForge — OSINT Toolkit

Toolkit for domain recon, JS analysis, secret scanning, attack surface mapping, and unified reporting. All tools by [brynnnn12](https://github.com/brynnnn12).

## Tools overview

| Tool | Category | Dir | Purpose |
|---|---|---|---|---|
| EngageForge | Setup | `setup/engageforge/` | Pentest engagement folder structure generator |
| ReconForge | Recon | `recon/reconforge/` | Subdomains, hosts, URLs, whois |
| JSHunter | Recon | `recon/jshunter/` | JS file analysis, endpoint extraction |
| GitHubRecon | Recon | `recon/github_recon/` | GitHub leak/secret search |
| AttackSurfaceMapper | Recon | `recon/attacksurfacemapper/` | Endpoint classification, graph viz |
| ScanForge | Scan | `scan/scanforge/` | Automated nmap + nuclei scanner |
| ReportHub | Report | `report/reporthub/` | Unified report + dashboard |
| **Pipeline** | — | root `pipeline.py` | Run all 7 tools in sequence |

## Quick start

```bash
# One-command install — creates .venv, installs all deps
./install.sh

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows CMD

# Run individual tools
python recon/reconforge/recon.py -d example.com --all --json
python recon/jshunter/jshunter.py -u https://example.com/app.js --json
python recon/github_recon/github_recon.py -d example.com --json
python setup/engageforge/engageforge.py -t example.com
python scan/scanforge/scanforge.py -i output/example.com
```

## Pipeline (`pipeline.py`)

Runs all 5 tools in sequence with a shared workspace at `workspace/{domain}/`:

```
workspace/{domain}/
├── recon/        ← ReconForge (subdomains, hosts, urls, whois)
├── jshunter/     ← JSHunter (endpoints, graphql, frameworks, etc.)
├── asm/          ← ASM (report.json, attack_surface.png)
├── scan/         ← ScanForge (nmap + nuclei)
└── report/       ← ReportHub (dashboard, report)
```

Flags: `--skip-recon`, `--skip-jshunter`, `--skip-asm`, `--skip-scanforge`, `--skip-reporthub`.

## Important constraints

- Python 3.10+ required.
- Single `.venv/` at root — created by `./install.sh`.
- Per-tool deps in `requirements/*.txt`, all installed into root `.venv`.
- Output is written to `workspace/{domain}/` by the pipeline, or to `output/{domain}/` per tool.
- `.venv/`, `__pycache__/`, `output/`, `reports/`, `logs/`, `workspace/` are gitignored.
- All tools require internet access.
- Author: [brynnnn12](https://github.com/brynnnn12)
