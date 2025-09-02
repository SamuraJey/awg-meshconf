VENV ?= .venv

pretty:
	$(VENV)/bin/ruff check --fix-only .
	$(VENV)/bin/ruff format .

ruff-lint:
	$(VENV)/bin/ruff check .

mypy:
	$(VENV)/bin/mypy .

lint: ruff-lint mypy

test:
	$(VENV)/bin/pytest ./tests

test-cov:
	$(VENV)/bin/pytest ./tests --cov=awg_meshconf --cov=./tests --cov-report term-missing --cov-fail-under=85