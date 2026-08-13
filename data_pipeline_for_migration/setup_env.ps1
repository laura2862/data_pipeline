# Create a local virtual environment and install every Python dependency.
# Usage: powershell -ExecutionPolicy Bypass -File .\setup_env.ps1

$ErrorActionPreference = "Stop"

$PythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "py" }
$VenvDir = if ($env:VENV_DIR) { $env:VENV_DIR } else { ".venv" }

try {
    if ($PythonBin -eq "py") {
        $Version = & py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        $PythonArgs = @("-3")
    }
    else {
        $Version = & $PythonBin -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        $PythonArgs = @()
    }
}
catch {
    throw "Python was not found. Install Python 3.11-3.13, then rerun this script."
}

if ($Version -notin @("3.11", "3.12", "3.13")) {
    throw "Unsupported Python $Version. Use Python 3.11, 3.12, or 3.13."
}

if (-not (Test-Path $VenvDir)) {
    & $PythonBin @PythonArgs -m venv $VenvDir
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt

@'
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
'@ | & $VenvPython

Write-Host ""
Write-Host "Environment is ready. Activate it with: .\.venv\Scripts\Activate.ps1"
Write-Host "Run the pipeline with: python main.py"
Write-Host "For database extraction, also install Microsoft ODBC Driver 17+ for SQL Server"
Write-Host "and ensure you can reach the BNS database network."
