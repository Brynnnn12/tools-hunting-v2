# AttackSurfaceMapper (ASM)

Endpoint classification, asset mapping, and attack surface visualization.

**Author: [brynnnn12](https://github.com/brynnnn12) | Version: 1.0**

## Features

- Asset mapping from ReconForge + JSHunter output
- Endpoint classification (auth, API, admin, upload, graphql, etc.)
- Attack surface correlation host → endpoint → category
- Graph visualization (networkx + matplotlib)
- Reports: JSON, HTML, CSV

## Installation

```bash
python -m venv .venv
# Linux/Mac: source .venv/bin/activate
# Windows:   .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python asm.py -h
python asm.py -i input_dir/ --all
python asm.py -i input_dir/ --html --json --graph
python asm.py --version
```

Input directory should contain files from ReconForge (`subdomains.txt`, `hosts.txt`, `urls.txt`) and JSHunter (`endpoints.txt`, `frameworks.txt`, etc.). The pipeline handles this automatically.

## Output

```
reports/
  report.json
  report.html
  assets.csv
  attack_surface.png
```

## Project Structure

```
attacksurfacemapper/
  asm.py        — CLI entrypoint
  core/         — config, logger, utils
  modules/      — parser, classifier, mapper, visualizer, reporter, statistics
  templates/    — report.html (Jinja2)
  reports/      — generated reports
```
