PYTHON=python3.7
PYFLAGS=-W ignore::DeprecationWarning
VERSION=`python setup.py --version`

install:
	python -m pip install -r requirements.txt
	echo "black . --line-length=120" > .git/hooks/pre-commit

test: install flake
	pytest tests

flake:
	flake8
