.ONESHELL:

EXCLUDED_DIRS := -path "./temp__src" -o -path "./venv" -o -path "./env" -o -path "./.venv" -o -path "./.env" -path "./.git" -o -path "./.mypy_cache" -o -path "./.pytest_cache" -o -path "./.coverage" -o -path "./.ruff_cache"
PYTHON_FILES := $(shell find . -type d \( $(EXCLUDED_DIRS) \) -prune -o -type f -name "*.py" -print)
YAML_FILES := $(shell find . -type d \( $(EXCLUDED_DIRS) \) -prune -o -type f \( -name "*.yaml" -o -name "*.yml" \) -print)
CACHE_DIRS := .mypy_cache .pytest_cache .coverage .ruff_cache

.PHONY: help
help:
	@echo "Available options:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

.PHONY: all
all: help

.PHONY: lint-with-mypy
lint-with-mypy:
	@echo "Running mypy..."
	@mypy ark/

.PHONY: lint-with-black
lint-with-black:
	@echo "Running black..."
	@if [ -n "$(PYTHON_FILES)" ]; then \
		black --check $(PYTHON_FILES); \
	else \
		echo "No Python files found. Skipping black."; \
	fi

.PHONY: lint-with-pylint
lint-with-pylint:
	@echo "Running pylint..."
	@pylint ark/

.PHONY: lint-with-ruff
lint-with-ruff:
	@echo "Running ruff..."
	@ruff ark/

.PHONY: check-toml
check-toml:
	@echo "Checking pyproject.toml with Poetry..."
	@poetry check

# Public commands below.

.PHONY: lint-python
lint-python: lint-with-black lint-with-ruff lint-with-mypy lint-with-pylint ## Run Python linters.

.PHONY: lint-ansible
lint-ansible: ## Run Ansible lint on all YAML files.
	@echo "Running ansible-lint..."
	@if [ -n "$(YAML_FILES)" ]; then ansible-lint $(YAML_FILES); else echo "No YAML files found. Skipping ansible-lint."; fi


.PHONY: clean
clean: ## Remove cache objects.
	@echo "Removing cache objects $(CACHE_DIRS)"
	@rm -rf $(CACHE_DIRS)

.PHONY: check-version
check-version: ## Check version definition.
	@echo "Checking Ark version definition consistency..."
	@VERSION_TOML=$$(grep -oP '(?<=^version = ")[^"]+' pyproject.toml) && \
	 VERSION_INIT=$$(grep -oP '(?<=__version__ = ")[^"]+' ark/__init__.py) && \
	 if [ "$$VERSION_TOML" != "$$VERSION_INIT" ]; then
	 	echo "Version mismatch between pyproject.toml ($$VERSION_TOML) and ark/__init__.py ($$VERSION_INIT)"; \
	 	exit 1; \
	 else \
	 	echo "  Found: $$VERSION_TOML"; \
	 fi

.PHONY: set-version
set-version: ## Set Ark version.
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make set-version VERSION=<new_version>"; \
		exit 1; \
	fi
	@echo "Setting version to $(VERSION)..."
	@sed -i -E '/^\[tool.poetry\]$$/,/^\[/ s/(version = ")[^"]+/\1$(VERSION)/' pyproject.toml
	@sed -i -E 's/(__version__ = ")[^"]+/\1$(VERSION)/' ark/__init__.py

	@$(MAKE) -s check-version

.PHONY: build
build: lint-python check-version check-toml lint-python clean ## Build Ark.
	@echo "Building package..."
	@poetry build

.PHONY: install
install: ## Install Ark in development mode.
	@echo "Installing Ark..."
	@poetry install

.PHONY: docs
docs: ## Build documentation.
	@echo "Building documentation..."
	@cd docs
	@rm -rf _build
	@poetry run sphinx-build -b html source _build
