# AttackSurfaceMapper (ASM)

AttackSurfaceMapper adalah framework analisis attack surface yang menerima hasil dari ReconForge dan JSHunter, kemudian mengorganisasi, mengklasifikasi, dan memvisualisasikan asset aplikasi web menjadi laporan yang mudah dipahami.

## Features

- Asset mapping dari hasil ReconForge dan JSHunter
- Endpoint classification ke kategori penting
- Attack surface analysis dan ringkasan statistik
- Correlation engine untuk host → endpoint → kategori
- Reporting JSON/HTML dan visualisasi graph

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python asm.py -h
python asm.py -i recon_output/
python asm.py -i recon_output/ --html
python asm.py -i recon_output/ --json
python asm.py -i recon_output/ --graph
python asm.py -i recon_output/ --all
```

## Screenshots

- Placeholder for CLI output
- Placeholder for report HTML
- Placeholder for graph visualization

## Project Structure

```
attacksurfacemapper/
  asm.py
  core/
  modules/
  templates/
  output/
  reports/
  logs/
```

## Output Examples

```
reports/
  report.json
  report.html
  assets.csv
  attack_surface.png
```

## Roadmap v2

- Technology Correlation
- Cloud Asset Mapping
- Asset Risk Scoring
- Interactive Dashboard
- PDF Reporting
