PYTHON=python3.8
VERSION=`python setup.py --version`

install:
	python -m pip install -U setuptools pip
	python -m pip install -Ur requirements.txt

test: install
	pytest tests

init_db:
	python -m scripts.database

emulate_players:
	python -m scripts.players_emulator

serve: install
	uvicorn explorebaduk.main:app --reload --port=8080
