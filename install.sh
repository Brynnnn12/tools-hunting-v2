#!/usr/bin/env bash
#
# BugBountySuite — Root Installer
# Unified virtual environment for all tools.
# Usage: ./install.sh
# Logs:  logs/install.log
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="logs"
LOG_FILE="$LOG_DIR/install.log"
VENV_DIR=".venv"
REQ_DIR="requirements"

PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=10

# ── Colours ──────────────────────────────────────────────────────
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ── Helpers ──────────────────────────────────────────────────────
log()  { echo -e "${GREEN}[✓]${NC} $*" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[!]${NC} $*" | tee -a "$LOG_FILE"; }
error(){ echo -e "${RED}[✗]${NC} $*" | tee -a "$LOG_FILE"; exit 1; }
info() { echo -e "${CYAN}[i]${NC} $*" | tee -a "$LOG_FILE"; }
header(){ echo -e "\n${BOLD}━━━ $* ━━━${NC}\n" | tee -a "$LOG_FILE"; }

# ── Entry banner ─────────────────────────────────────────────────
echo -e "${BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   BBBB   RRRR   Y   Y  N   N  N   N  N   N  N   N        ║
║   B   B  R   R   Y Y   NN  N  NN  N  NN  N  NN  N        ║
║   BBBB   RRRR     Y    N N N  N N N  N N N  N N N        ║
║   B   B  R  R     Y    N  NN  N  NN  N  NN  N  NN        ║
║   BBBB   R   R    Y    N   N  N   N  N   N  N   N        ║
║                                                          ║
║                 Setup — Installer                        ║
║              Unified Virtual Environment                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝${NC}"

# ── Setup log dir ───────────────────────────────────────────────
mkdir -p "$LOG_DIR"
: > "$LOG_FILE"

exec 3>&1 4>&2
# Also tee all output to log
exec > >(tee -a "$LOG_FILE") 2>&1

# ── 1. Python version check ─────────────────────────────────────
header "1/5  Validating Python"

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [[ -z "$PYTHON" ]]; then
    error "Python not found. Install Python $PYTHON_MIN_MAJOR.$PYTHON_MIN_MINOR+ first."
fi

PY_VER="$("$PYTHON" --version 2>&1 | awk '{print $2}')"
PY_MAJOR="$(echo "$PY_VER" | cut -d. -f1)"
PY_MINOR="$(echo "$PY_VER" | cut -d. -f2)"

if [[ "$PY_MAJOR" -lt "$PYTHON_MIN_MAJOR" ]] || \
   [[ "$PY_MAJOR" -eq "$PYTHON_MIN_MAJOR" && "$PY_MINOR" -lt "$PYTHON_MIN_MINOR" ]]; then
    error "Python $PYTHON_MIN_MAJOR.$PYTHON_MIN_MINOR+ required (found $PY_VER)"
fi

log "Python $PY_VER — OK"

# ── 2. Create virtual environment ───────────────────────────────
header "2/5  Creating virtual environment"

if [[ -d "$VENV_DIR" ]]; then
    warn ".venv already exists — skipping creation"
else
    "$PYTHON" -m venv "$VENV_DIR"
    log "Created .venv"
fi

# Determine activate path (Linux/macOS vs Windows Git Bash)
if [[ -f "$VENV_DIR/Scripts/activate" ]]; then
    ACTIVATE="$VENV_DIR/Scripts/activate"
else
    ACTIVATE="$VENV_DIR/bin/activate"
fi

source "$ACTIVATE"

# ── 3. Upgrade pip ──────────────────────────────────────────────
header "3/5  Upgrading pip"

pip install --upgrade pip --quiet
log "pip upgraded"

# ── 4. Install dependencies ─────────────────────────────────────
header "4/5  Installing dependencies"

TOOLS=(
    "reconforge"
    "jshunter"
    "github_recon"
    "attacksurfacemapper"
    "reporthub"
)

for tool in "${TOOLS[@]}"; do
    req_file="$REQ_DIR/$tool.txt"
    if [[ ! -f "$req_file" ]]; then
        warn "requirements/$tool.txt not found — skipping"
        continue
    fi
    info "Installing $tool..."
    pip install -r "$req_file" --quiet
    log "$tool — done"
done

# scanforge & engageforge are stdlib-only — no deps to install
info "ScanForge + EngageForge — no external deps (stdlib only)"

# ── 5. Finish ───────────────────────────────────────────────────
header "5/5  Verifying installation"

"$PYTHON" -c "
import sys, subprocess
reqs = {
    'reconforge':   ['rich','dns','requests','whois'],
    'jshunter':     ['rich','requests','jinja2'],
    'github_recon': ['requests'],
    'asm':          ['rich','jinja2','networkx','matplotlib'],
    'reporthub':    ['rich','jinja2','pandas','plotly','matplotlib'],
}
ok, fail = True, []
for tool, pkgs in reqs.items():
    for pkg in pkgs:
        try:
            __import__(pkg.replace('-','_'))
        except ImportError:
            fail.append(f'{tool}: {pkg}')
            ok = False
if ok:
    print('[✓] All dependencies verified successfully')
else:
    print('[!] Missing packages:')
    for f in fail:
        print(f'    - {f}')
    sys.exit(1)
"

echo ""
echo ""
echo -e "        ${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo -e "        ║                 INSTALLATION COMPLETE                            ║"
echo -e "        ╠══════════════════════════════════════════════════════════════════╣"
echo -e "        ║  ${CYAN}Log     :${NC} $LOG_FILE                                ║"
echo -e "        ║  ${CYAN}Activate:${NC} source .venv/bin/activate                 ║"
echo -e "        ║                        .venv\\Scripts\\activate                  ║"
echo -e "        ║  ${YELLOW}Token :${NC}  export GITHUB_TOKEN=ghp_xxx              ║"
echo -e "        ║  ${GREEN}Run    :${NC}  python pipeline.py -d example.com        ║"
echo -e "        ╚══════════════════════════════════════════════════════════════════╝${NC}"
