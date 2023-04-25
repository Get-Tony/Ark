# Tool configuration is handled in the pyproject.toml file.
# Author: Anthony Pagan <get-tony@outlook.com>

EXCLUDED_DIRS := -path "./temp__src" -o -path "./venv" -o -path "./env" -o -path "./.venv" -o -path "./.env" -path "./.git" -o -path "./.mypy_cache" -o -path "./.pytest_cache" -o -path "./.coverage" -o -path "./.ruff_cache"
PYTHON_FILES := $(shell find . -type d \( $(EXCLUDED_DIRS) \) -prune -o -type f -name "*.py" -print)
YAML_FILES := $(shell find . -type d \( $(EXCLUDED_DIRS) \) -prune -o -type f \( -name "*.yaml" -o -name "*.yml" \) -print)

.PHONY: all lint lint-python lint-yaml lint-with-mypy lint-with-black lint-with-pylint lint-with-ruff lint-with-ansible wipe-cache checks_passed

all:
	@echo "Available options:"
	@echo "  - lint: Run Python and YAML linters"
	@echo "  - lint-python: Run Python linters"
	@echo "  - lint-yaml: Run YAML linters"
	@echo "  - wipe-cache: Remove cache directories"
	@echo "Example usage: make lint"

lint: lint-python lint-yaml

lint-python: lint-with-black lint-with-ruff lint-with-mypy lint-with-pylint checks_passed

lint-yaml: lint-with-ansible checks_passed

lint-with-mypy:
	@echo "Running mypy..."
	@mypy ark/

lint-with-black:
	@echo "Running black..."
	@black --check $(PYTHON_FILES)

lint-with-pylint:
	@echo "Running pylint..."
	@pylint ark/

lint-with-ruff:
	@echo "Running ruff..."
	@ruff ark/

lint-with-ansible:
	@echo "Running ansible-lint..."
	@ansible-lint $(YAML_FILES)

wipe-cache:
	@echo "Wiping cache..."
	@rm -rf .mypy_cache .pytest_cache .coverage .ruff_cache

checks_passed:
	@echo "All checks passed"
