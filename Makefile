.PHONY: build check clean install publish run test upgrade

build:
	uv build --wheel

check:
	curl -L https://gist.githubusercontent.com/hoofir/02feeb244aacc4e2ddb92aba15f1990b/raw/check.sh | sh

clean:
	rm -rf build dist *.egg-info .vscode .python-version .venv uv.lock __pycache__ .pytest_cache .ruff_cache .mypy_cache

install:
	uv sync --frozen

run:
	uv run python

test:
	uv run pytest

upgrade:
	uv sync --upgrade