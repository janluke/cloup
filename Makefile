.DEFAULT_GOAL := help

REMOVE = python scripts/remove.py
BROWSER = python scripts/browser.py
COPYTREE = python scripts/copytree.py

DOCS_HTML_DIR = docs/_build/html
DOCS_HTML_STATIC = $(DOCS_HTML_DIR)/_static

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
	mypy cloup --strict
	mypy tests examples

.PHONY: lint
lint: ## check code, tests and examples with flake8
	flake8 cloup tests examples

.PHONY: test
test: install ## run tests quickly with the default Python
	pytest --cov=cloup -vv

.PHONY: coverage
coverage: test ## check code coverage quickly with the default Python
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

.PHONY: clean-docs
clean-docs: ## clean the documentation
	$(MAKE) -C docs clean
	$(REMOVE) docs/autoapi

.PHONY: docs
docs: ## generate Sphinx HTML documentation
	$(MAKE) -C docs html

.PHONY: view-docs
view-docs: docs ## open the built docs in the default browser
	$(BROWSER) $(DOCS_HTML_DIR)/index.html

.PHONY: re-docs
re-docs: clean-docs view-docs ## (re)generate Sphinx HTML documentation from scratch

LIVE_DOCS = sphinx-autobuild docs $(DOCS_HTML_DIR) \
	--watch ./**.rst \
	--watch ./cloup/**.py \
	--ignore ./docs/autoapi/**.rst \
	--open-browser

.PHONY: live-docs
live-docs:   ## watch docs files and rebuild the docs when they change
	$(LIVE_DOCS)

.PHONY: live-docs-all
live-docs-all:   ## write all files (useful when working on html/css)
	$(LIVE_DOCS) -a

.PHONY: update-docs-static
update-docs-static:   ## copy docs static files into the build folder
	$(COPYTREE) docs/_static $(DOCS_HTML_STATIC)

.PHONY: update-docs-css
update-docs-css:   ## copy docs css files into the build folder
	$(COPYTREE) docs/_static/styles $(DOCS_HTML_STATIC)/styles

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
dist: clean-build ## builds source and wheel package
	python setup.py sdist bdist_wheel
	twine check dist/*

.PHONY: release
release: dist ## package and upload a release
	twine upload dist/*

.PHONY: test-release
test-release: dist   ## package and upload a release
	twine upload --repository testpypi dist/*

PIP_COMPILE := pip-compile --resolver=backtracking

.PHONY: pip-compile
pip-compile:  ## pin dependencies in requirements/ using the current env
	$(PIP_COMPILE) requirements/test.in
	$(PIP_COMPILE) requirements/docs.in
	$(PIP_COMPILE) requirements/dev.in

.PHONY: pip-upgrade
pip-upgrade:   ## upgrade pip and dependencies
	python -m pip install -U pip
	$(PIP_COMPILE) --upgrade requirements/test.in
	# $(PIP_COMPILE) --upgrade requirements/docs.in
	$(PIP_COMPILE) --upgrade requirements/dev.in

.PHONY: pip-sync
pip-sync:  ## sync development environment with requirements/dev.txt
	pip install -U pip-tools
	pip-sync requirements/dev.txt
	pip install -e .
