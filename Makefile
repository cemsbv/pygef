SHELL=/bin/bash
PYTHON=venv/bin/python
PYTHON_BIN=venv/bin

.PHONY: pre-commit test clean mypy lint

venv:
	@python -m venv venv
	@venv/bin/pip install -U pip
	@venv/bin/pip install -r requirements.txt
	@venv/bin/pip install .

clean:
	@rm -r venv

test: venv
	$(PYTHON_BIN)/pytest pygef/tests/gef/**

pre-commit: mypy
	$(PYTHON_BIN)/black .

mypy: venv
	$(PYTHON_BIN)/mypy pygef

lint: mypy

