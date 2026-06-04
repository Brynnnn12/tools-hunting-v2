# ReportHub

ReportHub adalah reporting engine yang menggabungkan hasil dari ReconForge, JSHunter, dan AttackSurfaceMapper untuk menghasilkan laporan HTML, JSON, dan dashboard interaktif.

## Features

- Parsing output dari ReconForge, JSHunter, dan ASM
- Data aggregation dan statistik ringkas
- Visualisasi chart berbasis matplotlib
- Dashboard interaktif dengan Plotly
- HTML report modern dan JSON report

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python reporthub.py -h
python reporthub.py -i output/target.com
python reporthub.py -i output/target.com --html
python reporthub.py -i output/target.com --json
python reporthub.py -i output/target.com --dashboard
python reporthub.py -i output/target.com --all
```

## Project Structure

```
reporthub/
  reporthub.py
  core/
  modules/
  templates/
  reports/
  output/
  logs/
```

## Dashboard Screenshots

- Placeholder for dashboard screenshot

## Output Examples

```
reports/
  report.html
  report.json
  dashboard.html
  endpoint_chart.png
  framework_chart.png
```

## Roadmap v2

- PDF Report
- Multi Target Dashboard
- Historical Comparison
- Trend Analysis
- Executive Export
