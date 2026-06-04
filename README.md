# ReconForge Toolkit Suite

Unified OSINT and JavaScript analysis toolkit for recon workflows. This workspace contains four Python projects and a pipeline runner that chains them together:

- ReconForge: subdomains, hosts, URLs, whois
- JSHunter: JavaScript analysis and endpoint extraction
- AttackSurfaceMapper (ASM): asset mapping and endpoint classification
- ReportHub: unified reporting and dashboard

> Note: This suite does not perform vulnerability scanning, brute force, or exploitation. It focuses on discovery, analysis, visualization, and reporting.

## Requirements

- Python 3.12+
- Internet access for recon and HTTP downloads

## Quick Start

```bash
# Install deps for each tool
cd reconforge; pip install -r requirements.txt
cd ..\jshunter; pip install -r requirements.txt
cd ..\attacksurfacemapper; pip install -r requirements.txt
cd ..\reporthub; pip install -r requirements.txt

# Run the full pipeline
cd ..
python pipeline.py -d example.com
```

## Pipeline Usage

```bash
python pipeline.py -d example.com
python pipeline.py -d example.com --skip-jshunter
python pipeline.py -d example.com --skip-recon --skip-asm
```

Pipeline output layout:

```
workspace/{domain}/
├── recon/     # ReconForge output (subdomains, hosts, urls, whois)
├── jshunter/  # JSHunter output (endpoints, graphql, frameworks)
├── asm/       # ASM output (report, graph)
└── report/    # ReportHub output (dashboard, report)
```

## Individual Tools

### ReconForge

```bash
cd reconforge
python recon.py -d example.com --all --json
```

### JSHunter

```bash
cd jshunter
python jshunter.py -u https://example.com/app.js
python jshunter.py -f js.txt --json --html
```

### AttackSurfaceMapper (ASM)

```bash
cd attacksurfacemapper
python asm.py -i path\to\input --all
```

### ReportHub

```bash
cd reporthub
python reporthub.py -i output\target.com --all
```

## Notes

- The pipeline tries to auto-detect JS URLs from ReconForge output.
- If no JS URLs are found, run JSHunter manually with `-u` or `-f`.
- Reports and charts are generated in each tool's `reports/` folder and copied into `workspace/{domain}` by the pipeline.

## Project Structure

```
.
├── reconforge/
├── jshunter/
├── attacksurfacemapper/
├── reporthub/
├── pipeline.py
└── workspace/
```

## Roadmap

- Improve auto-correlation across tools
- Add historical trend view to ReportHub
- Add richer asset graph in ASM

## License

See [LICENSE](LICENSE).
