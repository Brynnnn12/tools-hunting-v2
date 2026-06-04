# ReconForge

ReconForge adalah framework recon OSINT dan asset management untuk target yang memiliki izin pengujian. Modular, multi-source, dengan output TXT/JSON/HTML.

## Fitur

- **Subdomain enumeration** — crt.sh, DNS brute force, Sublist3r, Subfinder, Assetfinder, Amass
- **Host resolution** — DNS A-record lookup + dnsx
- **URL probing** — requests + httpx + gau + waybackurls + katana (otomatis probing HTTP)
- **Whois lookup** — python-whois (fallback ke system whois)
- **Laporan** — TXT, JSON, HTML (dark theme)
- CLI berbasis argparse, progress bar dengan rich, logging ke file

## Instalasi

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Penggunaan

```bash
python recon.py -h
python recon.py -d example.com --all --json --html
python recon.py -d example.com --subdomains --whois
python recon.py -d example.com --hosts
python recon.py -d example.com --urls
python recon.py -d example.com --report
```

### Opsi CLI

```
-d, --domain   Target domain (wajib)
-o, --output   Output root (default: output)
--all          Jalankan semua modul
--subdomains   Jalankan modul subdomains
--hosts        Jalankan modul hosts
--urls         Jalankan modul urls
--whois        Jalankan modul whois
--report       Generate report
--json         Export JSON
--html         Export HTML report (hanya jika --report atau --all)
--version      Tampilkan versi
```

Semua modul tanpa tool eksternal tetap jalan (skip otomatis). Untuk hasil maksimal di Kali:

```bash
sudo apt install subfinder assetfinder amass dnsx httpx gau waybackurls katana
pip install sublist3r
```

## Output

```
output/example.com/
  subdomains.txt / .json
  hosts.txt      / .json
  urls.txt       / .json
  whois.txt      / .json
  report.txt     / .json / .html
  reconforge.log
```

## Output structure
Menggunakan `ThreadPoolExecutor` (20–30 workers) untuk concurrent lookups dengan DNS timeout 5 detik.

## Catatan

- Gunakan hanya untuk target yang sudah memiliki izin pengujian.
- ReconForge tidak menyediakan exploit, scanner kerentanan, brute force kredensial, atau fungsi ofensif.
- Semua tool eksternal bersifat opsional — modul tetap berjalan tanpa error jika tools tidak terinstall.
- Modul whois akan fallback ke system whois jika python-whois tidak tersedia.
