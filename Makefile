PYTHON=python3.7
PYFLAGS=-W ignore::DeprecationWarning
VERSION=`python setup.py --version`

install:
	python -m pip install -r requirements.txt

test: install flake
	pytest tests

flake:
	flake8
