# ReportHub

Unified reporting engine — combines ReconForge, JSHunter, and AttackSurfaceMapper results.

**Author: [brynnnn12](https://github.com/brynnnn12) | Version: 1.0**

## Features

- Parses ReconForge, JSHunter, and ASM output
- Data aggregation and summary statistics
- Matplotlib charts (endpoint categories, framework distribution)
- Interactive Plotly dashboard
- Reports: HTML, JSON, dashboard

## Installation

```bash
python -m venv .venv
# Linux/Mac: source .venv/bin/activate
# Windows:   .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python reporthub.py -h
python reporthub.py -i workspace/domain/ --all
python reporthub.py -i workspace/domain/ --html --json
python reporthub.py -i workspace/domain/ --dashboard
python reporthub.py --version
```

Input directory should have `recon/`, `jshunter/`, and `asm/` subdirectories. The pipeline handles this automatically.

## Output

```
reports/
  report.html
  report.json
  dashboard.html
  endpoint_chart.png
  framework_chart.png
```

## Project Structure

```
reporthub/
  reporthub.py   — CLI entrypoint
  core/          — config, logger, utils
  modules/       — parser, aggregator, statistics, visualizer, dashboard, reporter
  templates/     — report.html, dashboard.html (Jinja2)
  reports/       — generated reports
```
