@echo off

call venv/Scripts/activate.bat
python -m pip install -U -r requirements.txt
python -m uvicorn explorebaduk.main:app --reload --port=8080
