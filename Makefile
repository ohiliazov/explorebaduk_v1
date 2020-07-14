PYTHON=python3.7
VERSION=`python setup.py --version`
LDFLAGS='-L/usr/local/lib -L/usr/local/opt/openssl/lib -L/usr/local/opt/readline/lib'

install:
	python -m pip install -r requirements.txt

flake:
	flake8

black: flake
	black . --line-length=120

test: install black
	pytest tests

init_db:
	python -m scripts.database

serve:
	python run_api.py --host 0.0.0.0 --port 8080 --debug
