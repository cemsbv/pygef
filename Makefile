SHELL=/bin/bash
PYTHON=venv/bin/python
PYTHON_BIN=venv/bin

.PHONY: pre-commit test clean

venv:
	@python -m venv venv
	@venv/bin/pip install -U pip
	@venv/bin/pip install -r requirements.txt

clean:
	@rm -r venv

test: venv
	$(PYTHON_BIN)/pytest pygef/*
	$(PYTHON_BIN)/pytest pygef/robertson/*
	$(PYTHON_BIN)/pytest pygef/been_jefferies/*

pre-commit: venv
	$(PYTHON_BIN)/black .
