# 🛡️ BugBountySuite — OSINT & Recon Toolkit

Suite alat untuk bug bounty recon, analisis JavaScript, secret scanning, visualisasi attack surface, dan pelaporan terpadu. Dibangun oleh [brynnnn12](https://github.com/brynnnn12).

---

## 📦 Komponen

| Tool | Kategori | Lokasi | Fungsi |
|---|---|---|---|
| **EngageForge** | Setup | `setup/engageforge/` | Generate struktur folder engagement pentest |
| **ReconForge** | Recon | `recon/reconforge/` | Subdomain enumeration, host discovery, URL scraper, whois |
| **JSHunter** | Recon | `recon/jshunter/` | Analisis file JS, ekstraksi endpoint, graphql, storage, dll |
| **GitHubRecon** | Recon | `recon/github_recon/` | Pencarian secret/leak di GitHub |
| **AttackSurfaceMapper** | Recon | `recon/attacksurfacemapper/` | Klasifikasi endpoint, visualisasi graph jaringan |
| **ScanForge** | Scan | `scan/scanforge/` | Pemindaian otomatis nmap + nuclei |
| **ReportHub** | Report | `report/reporthub/` | Dashboard interaktif & laporan HTML/JSON terpadu |
| **Pipeline** | Orkestrasi | `pipeline.py` | Menjalankan seluruh tool secara berurutan dalam 1 perintah |

---

## 🚀 Quick Start

```bash
# 1. Install semua dependency (cukup sekali)
./install.sh

# 2. Aktifkan virtual environment
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows CMD

# 3. Jalankan pipeline untuk target
python pipeline.py -d example.com

# Atau jalankan tool secara individual
python recon/reconforge/recon.py -d example.com --all --json
```

---

## 🔧 Instalasi Detail

### Persyaratan

- **Python 3.10+**
- Koneksi internet
- (Opsional) `nmap` & `nuclei` di PATH untuk ScanForge

### Cara Kerja Installer (`./install.sh`)

| Tahap | Aksi |
|---|---|
| 1/5 | Validasi Python 3.10+ |
| 2/5 | Membuat `.venv` di root (skip jika sudah ada) |
| 3/5 | Upgrade pip ke versi terbaru |
| 4/5 | Install dependencies dari `requirements/*.txt` |
| 5/5 | Verifikasi semua import berhasil |

Semua output dicatat ke `logs/install.log`.

### Struktur Dependency

```
requirements/
├── reconforge.txt           # rich, dnspython, requests, python-whois
├── jshunter.txt             # rich, requests, jinja2
├── github_recon.txt         # requests
├── attacksurfacemapper.txt  # rich, jinja2, networkx, matplotlib
└── reporthub.txt            # rich, jinja2, pandas, plotly, matplotlib
```

> **Catatan**: ScanForge & EngageForge hanya menggunakan stdlib — tidak perlu installasi tambahan.

---

## 🧪 Penggunaan Per Tool

### EngageForge — Setup Struktur Folder

```bash
python setup/engageforge/engageforge.py -t example.com
python setup/engageforge/engageforge.py -t example.com -o ~/projects
```

Generate folder structure untuk engagement pentest.

### ReconForge — Subdomain & Host Discovery

```bash
python recon/reconforge/recon.py -d example.com --all --json --html
python recon/reconforge/recon.py -d example.com --subdomains --whois
```

Output: subdomains, live host, all URLs, whois info → `output/{domain}/`

### JSHunter — Analisis JavaScript

```bash
python recon/jshunter/jshunter.py -u https://example.com/app.js
python recon/jshunter/jshunter.py -f js_urls.txt --json --html
python recon/jshunter/jshunter.py -i output/example.com
python recon/jshunter/jshunter.py -d ./static/js
```

Mendeteksi: endpoint API, path GraphQL, WebSocket, storage (localStorage/indexedDB), framework, keyword sensitif.

### GitHubRecon — Pencarian Secret/Leak

```bash
python recon/github_recon/github_recon.py -d example.com --json
set GITHUB_TOKEN=ghp_xxx  # Windows CMD
export GITHUB_TOKEN=ghp_xxx  # Linux/macOS
python recon/github_recon/github_recon.py -d example.com --json
```

Cari secret, API key, credential yang ter-expose di GitHub.

### AttackSurfaceMapper — Klasifikasi & Visualisasi

```bash
python recon/attacksurfacemapper/asm.py -i path/to/input --all
python recon/attacksurfacemapper/asm.py -i path/to/input --html --graph
```

Input: `subdomains.txt`, `live.txt`, `all_urls.txt`, `endpoints.txt`, dll.
Output: report HTML, grafik attack surface.

### ScanForge — Pemindaian Otomatis

```bash
python scan/scanforge/scanforge.py -i output/example.com --dry-run
python scan/scanforge/scanforge.py -i output/example.com -p full
python scan/scanforge/scanforge.py -f targets.txt
```

Membutuhkan `nmap` dan `nuclei` terinstall di sistem.

### ReportHub — Dashboard & Laporan

```bash
python report/reporthub/reporthub.py -i workspace/example.com --all
python report/reporthub/reporthub.py -i workspace/example.com --dashboard
```

Generate dashboard interaktif (Plotly) + laporan HTML/JSON.

---

## ⚙️ Pipeline

Menjalankan 6 tool secara otomatis dengan 1 perintah:

```bash
python pipeline.py -d example.com
python pipeline.py -d example.com --skip-recon --skip-jshunter
python pipeline.py -d example.com --skip-scanforge --skip-reporthub
python pipeline.py --help
```

### Struktur Output

```
workspace/{domain}/
├── recon/        ← ReconForge (subdomains, hosts, urls, whois)
├── jshunter/     ← JSHunter (endpoints, graphql, frameworks, dll)
├── asm/          ← AttackSurfaceMapper (report.json, attack_surface.png)
├── scan/         ← ScanForge (nmap + nuclei)
└── report/       ← ReportHub (dashboard.html, report.json)
```

### Flags

| Flag | Fungsi |
|---|---|
| `--skip-recon` | Skip ReconForge |
| `--skip-jshunter` | Skip JSHunter |
| `--skip-asm` | Skip AttackSurfaceMapper |
| `--skip-scanforge` | Skip ScanForge |
| `--skip-reporthub` | Skip ReportHub |

---

## ❗ Troubleshooting

| Masalah | Solusi |
|---|---|
| `./install.sh` gagal | Pastikan Python 3.10+ terinstall & tersedia di PATH |
| Output kosong | Periksa target valid & dalam scope yang diizinkan |
| GitHubRecon rate limit | Set environment variable `GITHUB_TOKEN=ghp_xxx` (limit 5000 req/jam) |
| ScanForge gagal | Install nmap (`sudo apt install nmap`) & nuclei |
| Module not found | Jalankan `pip install -r requirements/all.txt` |
| File input tidak ditemukan | Periksa path dan izin baca/tulis direktori |

---

## 🧹 Struktur Direktori Lengkap

```
BugBountySuite/
├── install.sh
├── pipeline.py
├── requirements/
│   ├── all.txt
│   ├── reconforge.txt
│   ├── jshunter.txt
│   ├── github_recon.txt
│   ├── attacksurfacemapper.txt
│   └── reporthub.txt
├── .venv/              # Virtual environment (auto-generated)
├── logs/               # Log installer
├── output/             # Output per tool
├── workspace/          # Output pipeline terpadu
├── reports/            # Laporan final
├── recon/
│   ├── reconforge/
│   ├── jshunter/
│   ├── github_recon/
│   └── attacksurfacemapper/
├── scan/
│   └── scanforge/
├── report/
│   └── reporthub/
└── setup/
    └── engageforge/
```

---

## 📄 Lisensi

Lihat [LICENSE](LICENSE).

---

> **Penulis**: [brynnnn12](https://github.com/brynnnn12) — Gunakan alat ini hanya pada target yang sah dan berizin.
