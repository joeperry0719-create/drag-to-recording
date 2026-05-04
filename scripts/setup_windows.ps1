$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -3.11 -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
python -m compileall screen_region_recorder
