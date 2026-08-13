#!/usr/bin/env bash
# Create a local virtual environment and install every Python dependency.
# Usage: bash setup_env.sh

set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python was not found. Install Python 3.11-3.13, then rerun this script."
  exit 1
fi

PYTHON_VERSION="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
case "$PYTHON_VERSION" in
  3.11|3.12|3.13) ;;
  *)
    echo "Unsupported Python $PYTHON_VERSION. Use Python 3.11, 3.12, or 3.13."
    exit 1
    ;;
esac

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

"$VENV_DIR/bin/python" - <<'PY'
import importlib

packages = {
    "pandas": "pandas",
    "numpy": "numpy",
    "sqlalchemy": "SQLAlchemy",
    "pyodbc": "pyodbc",
    "openpyxl": "openpyxl",
    "rapidfuzz": "rapidfuzz",
    "sklearn": "scikit-learn",
    "sparse_dot_topn": "sparse-dot-topn",
}

for module, package in packages.items():
    importlib.import_module(module)
    print(f"OK: {package}")
PY

echo
echo "Environment is ready. Activate it with: source $VENV_DIR/bin/activate"
echo "Run the pipeline with: python main.py"
echo "For database extraction, also install Microsoft ODBC Driver 17+ for SQL Server"
echo "and ensure you can reach the BNS database network."
