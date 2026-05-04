$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1
python -m pytest -q
python -m compileall screen_region_recorder
