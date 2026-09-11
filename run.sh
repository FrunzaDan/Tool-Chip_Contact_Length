#!/usr/bin/env bash
#
# Runs the Tool-Chip Contact Length (TCCL) application.
#
# What it does, in order:
#   1. Locates a usable Python 3 interpreter (and checks its version).
#   2. Checks which packages from requirements.txt are already installed,
#      and installs whatever is missing.
#   3. Runs the app (src/main.py) and logs everything to Logs/.
#
# Usage: ./run.sh

set -eu

# ---------------------------------------------------------------------------
# Setup: resolve paths so the script works from any working directory.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
LOG_DIR="$SCRIPT_DIR/Logs"
mkdir -p "$LOG_DIR"
RUN_LOG="$LOG_DIR/run_$(date +%Y-%m-%d_%H-%M-%S).log"

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$RUN_LOG"
}

log "===== TCCL run script started ====="

# ---------------------------------------------------------------------------
# Step 1: Find and validate a Python interpreter.
# ---------------------------------------------------------------------------
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=10

PYTHON_BIN=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    log "ERROR: No Python interpreter found on PATH (tried 'python3' and 'python')."
    log "Install Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ from https://www.python.org/downloads/ and try again."
    exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
log "Found Python interpreter: $(command -v "$PYTHON_BIN") (version $PYTHON_VERSION)"

if ! "$PYTHON_BIN" -c "import sys; sys.exit(0 if sys.version_info >= (${MIN_PYTHON_MAJOR}, ${MIN_PYTHON_MINOR}) else 1)"; then
    log "ERROR: Python $PYTHON_VERSION was found, but this app requires ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR} or newer."
    exit 1
fi

if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
    log "ERROR: pip is not available for $PYTHON_BIN. Install pip (e.g. '$PYTHON_BIN -m ensurepip') and try again."
    exit 1
fi

# ---------------------------------------------------------------------------
# Step 2: Check installed dependencies against requirements.txt, install
# whatever is missing.
# ---------------------------------------------------------------------------
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log "ERROR: requirements.txt not found at $REQUIREMENTS_FILE"
    exit 1
fi

log "Checking dependencies from requirements.txt..."
missing_packages=()

while IFS= read -r line || [ -n "$line" ]; do
    # Strip inline comments, then leading/trailing whitespace.
    line="${line%%#*}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue

    # Skip pip options (-e, -r, --hash=...) and direct URL/VCS requirements;
    # this script only checks plain "package[==version]" style entries.
    case "$line" in
        -*|http://*|https://*|git+*)
            log "  [SKIP] Not a plain package requirement, skipping check: $line"
            continue
            ;;
    esac

    # Extract the bare package name (before any version specifier / extras /
    # environment marker).
    pkg_name="$(printf '%s' "$line" | sed -E 's/[<>=!~;\[].*$//' | sed -e 's/[[:space:]]*$//')"
    [ -z "$pkg_name" ] && continue

    if "$PYTHON_BIN" -m pip show "$pkg_name" >/dev/null 2>&1; then
        installed_version="$("$PYTHON_BIN" -m pip show "$pkg_name" 2>/dev/null | awk -F': ' '/^Version:/ {print $2}')"
        log "  [OK]      $pkg_name ($installed_version) is already installed"
    else
        log "  [MISSING] $pkg_name is not installed"
        missing_packages+=("$pkg_name")
    fi
done < "$REQUIREMENTS_FILE"

if [ ${#missing_packages[@]} -gt 0 ]; then
    log "Installing missing dependencies (${missing_packages[*]}) from requirements.txt..."
    if "$PYTHON_BIN" -m pip install -r "$REQUIREMENTS_FILE" >>"$RUN_LOG" 2>&1; then
        log "Dependencies installed successfully."
    else
        log "ERROR: Failed to install dependencies. See $RUN_LOG for details."
        exit 1
    fi
else
    log "All dependencies are already installed."
fi

# ---------------------------------------------------------------------------
# Step 3: Run the application.
# ---------------------------------------------------------------------------
log "Starting the Tool-Chip Contact Length application..."
log "(Detailed per-image processing logs are written by the app itself to $LOG_DIR/TCCL_process_*.log)"

cd "$SCRIPT_DIR/src"

set +e
"$PYTHON_BIN" main.py 2>&1 | tee -a "$RUN_LOG"
exit_code=${PIPESTATUS[0]}
set -e

if [ "$exit_code" -eq 0 ]; then
    log "Application finished successfully."
else
    log "ERROR: Application exited with status $exit_code."
    exit "$exit_code"
fi

log "===== TCCL run script finished ====="
