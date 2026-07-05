.PHONY: bootstrap detect status list mcp-list test lint clean

bootstrap:
	@bash bootstrap bootstrap --profile notebook

detect:
	@bash bootstrap detect

status:
	@bash bootstrap status

list:
	@bash bootstrap list

mcp-list:
	@bash bootstrap mcp-list

test:
	@python -m pytest tests/ -v

lint:
	@python -m ruff check core/ tests/

format:
	@python -m ruff check --fix core/ tests/

clean:
	rm -rf .venv .state __pycache__ core/__pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

install-dev:
	pip install -e ".[dev]"
