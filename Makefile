# FED-LINk Makefile — shortcuts for the commands in BUILD.md.
#
# Usage:
#   make help       # list targets
#   make install    # runtime + dev dependencies
#   make build      # output/ + links.zip
#   make test       # pytest suite
#   make lint       # ruff check
#   make format     # ruff format
#   make clean      # generated artifacts + caches
#   make package    # desktop executable via pyinstaller.spec
#   make all        # lint + test + build

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
LINKS ?= configs/links.json
OUTPUT ?= output
ZIP ?= links.zip

.PHONY: help install install-dev build test lint format clean package all check verify list htaccess

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime dependencies (requirements.txt)
	$(PIP) install -r requirements.txt

install-dev:  ## Install runtime + dev dependencies
	$(PIP) install -r requirements.txt -r requirements-dev.txt

build:  ## Build the redirect bundle (output/ + links.zip)
	$(PYTHON) -m src.main build $(LINKS) --output $(OUTPUT) --zip $(ZIP)
	@echo "Built $(OUTPUT)/ and $(ZIP)"

test:  ## Run the pytest suite
	$(PYTHON) -m pytest

lint:  ## Run ruff check (config in pyproject.toml)
	$(PYTHON) -m ruff check src/ tests/ scripts/ examples/

format:  ## Run ruff format
	$(PYTHON) -m ruff format src/ tests/ scripts/ examples/

check:  ## Validate the links file without building
	$(PYTHON) -m src.main validate $(LINKS)

list:  ## List every slug -> destination pair
	$(PYTHON) -m src.main list $(LINKS)

htaccess:  ## Preview the generated .htaccess rules
	$(PYTHON) -m src.main generate-htaccess $(LINKS)

package:  ## Build the desktop executable (pyinstaller.spec)
	$(PIP) install pyinstaller
	pyinstaller pyinstaller.spec

clean:  ## Remove generated artifacts and caches (.keep files survive)
	rm -rf $(OUTPUT)
	rm -f $(ZIP)
	rm -rf .pytest_cache .ruff_cache dist/FED-LINk* build/FED-LINk*
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

all: lint test build  ## lint + test + build

verify: check list htaccess  ## validate + list + htaccess preview
