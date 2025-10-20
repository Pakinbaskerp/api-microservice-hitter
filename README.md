"""
# Run locally


# (1) Create venv and install deps
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -U pip
pip install -e . # or: pip install fastapi uvicorn[standard] httpx pydantic pydantic-settings


# (2) Start the gateway
# Use python -m to avoid the "can't open file 'uvicorn'" error on Windows
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


# (3) Open http://localhost:8000
"""