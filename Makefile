PYTHON=python3.7
VERSION=`python setup.py --version`
LDFLAGS='-L/usr/local/lib -L/usr/local/opt/openssl/lib -L/usr/local/opt/readline/lib'

install:
	python -m pip install --upgrade pip
	python -m pip install --upgrade -r requirements.txt

test: install black
	pytest tests

init_db:
	python -m scripts.database

serve:
	python run_api.py --host localhost --port 8080 --debug --auto-reload
