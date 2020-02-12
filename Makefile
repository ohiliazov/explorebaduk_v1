PYTHON=python3.7
VERSION=`python setup.py --version`

install:
	python -m pip install -r requirements.txt

flake:
	flake8

black: flake
	black . --line-length=120

test: install black
	pytest tests

init_db:
	python explorebaduk/utils/database.py
