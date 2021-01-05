.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

BROWSER = python scripts/browser.py

.PHONY: help
help:
	@python scripts/make-help.py < $(MAKEFILE_LIST)

.PHONY: install
install: clean ## install the package in dev mode
	pip install -e .

.PHONY: mypy
mypy: ## check code, tests and examples with mypy
	mypy cloup tests examples

.PHONY: lint
lint: ## check code, tests and examples with flake8
	flake8 cloup tests examples

.PHONY: test
test: ## run tests quickly with the default Python
	pytest

.PHONY: coverage
coverage: ## check code coverage quickly with the default Python
	coverage run --source cloup -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

.PHONY: docs
docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/cloup.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ cloup
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

.PHONY: viewdocs
viewdocs: docs ## compile the docs and view it in the default browser
	$(BROWSER) docs/_build/html/index.html

.PHONY: clean
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

.PHONY: dist
dist: clean ## builds source and wheel package
	python setup.py sdist bdist_wheel
	twine check dist/*

.PHONY: release
release: dist ## package and upload a release
	twine upload dist/*
