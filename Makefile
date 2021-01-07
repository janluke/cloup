.DEFAULT_GOAL := help

REMOVE = python scripts/remove.py
BROWSER = python scripts/browser.py

.PHONY: help
help:
	@python scripts/make-help.py < $(MAKEFILE_LIST)

.PHONY: venv
venv: ## creates a virtualenv using tox
	tox -e dev

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
	$(REMOVE) docs/cloup.rst docs/modules.rst
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
	$(REMOVE) build dist .eggs
	$(REMOVE) -r './**/*.egg-info'
	$(REMOVE) -r './**/*.egg'

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	$(REMOVE) -r './**/__pycache__'
	$(REMOVE) -r './**/*.pyc'
	$(REMOVE) -r './**/*.pyo'

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	$(REMOVE) .tox .coverage htmlcov .pytest_cache

.PHONY: dist
dist: clean ## builds source and wheel package
	python setup.py sdist bdist_wheel
	twine check dist/*

.PHONY: release
release: dist ## package and upload a release
	twine upload dist/*

.PHONY: pin-deps
pin-deps: ## pin dependencies in requirements/ using the current env
	pip-compile requirements/test.in
	pip-compile requirements/docs.in
	pip-compile requirements/dev.in
