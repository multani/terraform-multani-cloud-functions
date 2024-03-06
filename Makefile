DIRECTORIES = \
	multani \
	tests

requirements.txt: pyproject.toml poetry.lock
	poetry -V
	poetry export --format requirements.txt --output $@ --without-hashes

test:
	poetry run pytest

mypy:
	poetry run mypy

fmt:
	poetry run black $(DIRECTORIES)
	poetry run isort $(DIRECTORIES)

check:
	poetry run black --check $(DIRECTORIES)
	poetry run isort --check $(DIRECTORIES)
	poetry run ruff check $(DIRECTORIES)

lint:
	poetry run ruff $(DIRECTORIES)
