# ReconForge Toolkit Suite

Suite OSINT dan analisis JavaScript untuk workflow recon. Terdiri dari beberapa proyek Python mandiri dan satu pipeline yang mengorkestrasi semuanya.

**Penulis: [brynnnn12](https://github.com/brynnnn12)**

## Komponen

| Tool | Kategori | Direktori | Tujuan |
|---|---|---|---|---|
| EngageForge | Setup | `setup/engageforge/` | Generator struktur folder engagement pentest |
| ReconForge | Recon | `recon/reconforge/` | Subdomain, host, URL, whois |
| JSHunter | Recon | `recon/jshunter/` | Analisis JS, ekstraksi endpoint |
| GitHubRecon | Recon | `recon/github_recon/` | Pencarian leak/secret di GitHub |
| AttackSurfaceMapper | Recon | `recon/attacksurfacemapper/` | Klasifikasi endpoint, visualisasi graph |
| ScanForge | Scan | `scan/scanforge/` | Pemindaian otomatis nmap + nuclei |
| ReportHub | Report | `report/reporthub/` | Laporan terpadu + dashboard |
| Pipeline | Orkestrasi | `pipeline.py` | Menjalankan seluruh tool secara berurutan |

## Tujuan & Batasan

Suite ini fokus pada recon, analisis asset, visualisasi, dan reporting. Gunakan hanya pada target yang sah dan berizin. Beberapa modul (mis. ScanForge) melakukan pemindaian aktif; gunakan dengan kehati-hatian dan scope yang jelas.

## Persyaratan

- Python 3.12+
- Koneksi internet
- (Opsional) `nmap` dan `nuclei` untuk ScanForge

## Instalasi

Setiap tool memiliki `requirements.txt` sendiri. Instal per tool atau sekaligus:

```bash
# Install semua tool (yang punya requirements.txt)
cd recon/reconforge;          pip install -r requirements.txt; cd ../..
cd recon/jshunter;            pip install -r requirements.txt; cd ../..
cd recon/github_recon;        pip install -r requirements.txt; cd ../..
cd recon/attacksurfacemapper; pip install -r requirements.txt; cd ../..
cd report/reporthub;          pip install -r requirements.txt; cd ../..

# EngageForge & ScanForge tidak memiliki dependensi eksternal (hanya stdlib)
cd setup/engageforge; # no install needed; cd ../..
cd scan/scanforge;    # no install needed; cd ../..

# Virtual environment per tool (disarankan)
cd recon/reconforge
python -m venv .venv
# Linux/Mac: source .venv/bin/activate
# Windows:   .venv\Scripts\activate
pip install -r requirements.txt
# Ulangi untuk setiap tool
```

## Pipeline

Pipeline menjalankan urutan berikut:

ReconForge → GitHubRecon → JSHunter → ASM → ScanForge → ReportHub

Contoh penggunaan:

```bash
python pipeline.py -d example.com
python pipeline.py -d example.com --skip-github
python pipeline.py -d example.com --skip-recon --skip-asm
python pipeline.py -d example.com --skip-scanforge --skip-reporthub
python pipeline.py --help
```

Struktur output pipeline:

```
workspace/{domain}/
├── recon/     ← ReconForge (subdomains, hosts, urls, whois)
├── github/    ← GitHubRecon (secrets, leaks, repos)
├── jshunter/  ← JSHunter (endpoints, graphql, frameworks)
├── asm/       ← ASM (report, graph)
├── scan/      ← ScanForge (nmap + nuclei)
└── report/    ← ReportHub (dashboard, report)
```

## Input dan Output yang Diharapkan

- ReconForge menulis output ke folder domain (mis. `output/example.com`). Pipeline akan menyalinnya ke `workspace/{domain}/recon/`.
- JSHunter mendukung sumber input berikut:
	- `-u` URL JS tunggal
	- `-f` file daftar URL JS
	- `-i` folder output ReconForge (auto-detect JS URLs)
	- `-d` scan file `.js` lokal secara rekursif
- ASM membaca berkas gabungan di folder input (contoh yang umum):
	- `subdomains.txt`, `live.txt`, `all_urls.txt`, `endpoints.txt`, `graphql.txt`, `websockets.txt`, `storage.txt`, `frameworks.txt`, `keywords.txt`
- ReportHub membaca struktur:
	- `recon/`, `jshunter/`, `asm/` di dalam `workspace/{domain}/`

## Penggunaan per Tool

### EngageForge

```bash
cd setup/engageforge
python engageforge.py -t example.com
python engageforge.py -t target1 target2 target3
python engageforge.py -t example.com -o ~/projects
python engageforge.py --help
```

### ReconForge

```bash
cd recon/reconforge
python recon.py -d example.com --all --json --html
python recon.py -d example.com --subdomains --whois
python recon.py --help
```

### JSHunter

```bash
cd recon/jshunter
python jshunter.py -u https://example.com/app.js
python jshunter.py -f js_urls.txt --json --html
python jshunter.py -i path/to/reconforge/output
python jshunter.py -d ./static/js
python jshunter.py --help
```

### GitHubRecon

```bash
cd recon/github_recon
python github_recon.py -d example.com --json
python github_recon.py -d example.com --token ghp_xxx --json
python github_recon.py --help
```

### AttackSurfaceMapper (ASM)

```bash
cd recon/attacksurfacemapper
python asm.py -i path/to/input --all
python asm.py -i path/to/input --html --graph
python asm.py --help
```

### ScanForge

```bash
cd scan/scanforge
python scanforge.py -i path/to/reconforge/output --dry-run
python scanforge.py -i path/to/reconforge/output -p full
python scanforge.py -f targets.txt
python scanforge.py --help
```

### ReportHub

```bash
cd report/reporthub
python reporthub.py -i path/to/workspace --all
python reporthub.py -i path/to/workspace --dashboard
python reporthub.py --help
```

## Troubleshooting Singkat

- Output kosong: pastikan target valid dan berada dalam scope yang diizinkan.
- Rate limit GitHubRecon: gunakan `--token` agar limit 5000 req/jam.
- ScanForge gagal: pastikan `nmap` dan `nuclei` tersedia di PATH.
- Folder input tidak ditemukan: periksa path dan izin baca/tulis.

## Lisensi

Lihat [LICENSE](LICENSE).
