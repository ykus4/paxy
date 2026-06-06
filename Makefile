.PHONY: install run dev web-install web-build web-dev test lint clean docs-dev docs-build

install:
	uv sync

run:
	uv run python main.py

gui:
	uv run python main.py --mode gui

cui:
	uv run python main.py --mode cui

web-install:
	cd web && npm install

web-build:
	cd web && npm run build

web-dev:
	cd web && npm run dev

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check paxy/

clean:
	rm -rf __pycache__ paxy/**/__pycache__ .pytest_cache site/ web/dist/

docs-dev:
	mkdocs serve

docs-build:
	mkdocs build
