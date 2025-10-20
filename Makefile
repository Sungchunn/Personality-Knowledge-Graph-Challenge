.PHONY: setup ingest clean test lint format help

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PDF_ROOT := "/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Data"
OUT_ROOT := ./data

help:
	@echo "Personality Knowledge Graph - Ingestion Pipeline"
	@echo ""
	@echo "Available targets:"
	@echo "  make setup    - Create virtual environment and install dependencies"
	@echo "  make ingest   - Run full PDF ingestion pipeline"
	@echo "  make clean    - Remove generated outputs (text, jsonl, metadata)"
	@echo "  make test     - Run pytest suite"
	@echo "  make lint     - Run ruff linter"
	@echo "  make format   - Format code with black"
	@echo "  make link     - Create symlink to raw PDF directory"

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo ""
	@echo "Setup complete! Activate with: source $(VENV)/bin/activate"

link:
	bash scripts/link_raw.sh

ingest: setup
	$(BIN)/python -m src.ingest.cli \
		--pdf-root $(PDF_ROOT) \
		--out-root $(OUT_ROOT) \
		--ocr auto \
		--min-chars 1200 \
		--max-chars 2000 \
		--overlap 200

clean:
	rm -rf $(OUT_ROOT)/text/*
	rm -rf $(OUT_ROOT)/jsonl/*
	rm -rf $(OUT_ROOT)/metadata/*
	@echo "Cleaned all generated outputs"

clean-all: clean
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf src/**/__pycache__
	@echo "Cleaned all artifacts including venv"

test:
	$(BIN)/pytest -v

lint:
	$(BIN)/ruff check src/

format:
	$(BIN)/black src/
