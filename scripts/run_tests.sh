#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
python -m pytest -q
python -m compileall screen_region_recorder
