# ReconForge — OSINT Toolkit

Toolkit for domain recon, JS analysis, secret scanning, attack surface mapping, and unified reporting. All tools by [brynnnn12](https://github.com/brynnnn12).

## Tools overview

| Tool | Dir | Entrypoint | Purpose |
|---|---|---|---|
| ReconForge | `reconforge/` | `recon.py` | Subdomains, hosts, URLs, whois |
| JSHunter | `jshunter/` | `jshunter.py` | JS file analysis, endpoint extraction |
| GitHubRecon | `github_recon/` | `github_recon.py` | GitHub leak/secret search |
| AttackSurfaceMapper | `attacksurfacemapper/` | `asm.py` | Endpoint classification, graph viz |
| ReportHub | `reporthub/` | `reporthub.py` | Unified report + dashboard |
| **Pipeline** | root | `pipeline.py` | Run all 4 domain tools in sequence |

## Quick start

```bash
# Install deps for each tool
cd reconforge; pip install -r requirements.txt
cd ../jshunter; pip install -r requirements.txt
cd ../github_recon; pip install -r requirements.txt
cd ../attacksurfacemapper; pip install -r requirements.txt
cd ../reporthub; pip install -r requirements.txt

# Full pipeline (ReconForge → JSHunter → ASM → ReportHub)
cd ..; python pipeline.py -d example.com

# Individual tools
python reconforge/recon.py -d example.com --all --json
python jshunter/jshunter.py -u https://example.com/app.js --json
python github_recon/github_recon.py -d example.com --json
```

## Pipeline (`pipeline.py`)

Runs all 4 domain tools in sequence with a shared workspace at `workspace/{domain}/`:

```
workspace/{domain}/
├── recon/        ← ReconForge output (subdomains, hosts, urls, whois)
├── jshunter/     ← JSHunter output (endpoints, graphql, frameworks, etc.)
├── asm/          ← ASM output (report.json, attack_surface.png)
├── report/       ← ReportHub output (report.html, dashboard.html)
├── live.txt      ← copy for ASM
└── all_urls.txt  ← merged URLs for ASM
```

Flags: `--skip-recon`, `--skip-jshunter`, `--skip-asm`, `--skip-reporthub`.

## Important constraints

- Python 3.10+ required.
- Each tool has its own `requirements.txt` and `.venv/`.
- Output is written to `workspace/{domain}/` by the pipeline, or to `output/{domain}/` per tool.
- `.venv/`, `__pycache__/`, `output/`, `reports/`, `logs/`, `workspace/` are gitignored.
- All tools require internet access.
- Author: [brynnnn12](https://github.com/brynnnn12)
