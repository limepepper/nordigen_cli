.PHONY: clean build

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test

#install: clean ## install the package to the active Python's site-packages
#	python setup.py install

tox: ## run tox on docker compose
	@echo do tox stuff ## this is a comment
	tox

test: ## run run pytest
	poetry run pytest

docker-%: Makefile ## defer to docker subdir Makefile
	@$(MAKE) -C .docker $*

docker:  ## A target that delegates to a subdirectory
	$(MAKE) -C .docker $(COMMAND)

docs-%: Makefile
	@$(MAKE) -C docs $*

