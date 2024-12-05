# Minimal makefile for Sphinx documentation
#

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error "The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from https://sphinx-doc.org/")
endif

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

html:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html-show: html
	@$(BROWSER) build/html/index.html

livehtml:
	 sphinx-autobuild --open-browser \
 		--port=0 \
 		--watch ../src \
 		"$(SOURCEDIR)" \
 		"$(BUILDDIR)" \
 		$(SPHINXOPTS) $(O)

define BROWSER_GITSCRIPT
set -eu -o pipefail
git_dir="$$(git rev-parse --show-toplevel)"
git_dir_name="$$(basename $${git_dir})"
gh_pages_dir="$${git_dir}/../$${git_dir_name}_gh_pages"
mkdir -p "$${gh_pages_dir}"
if git worktree add "$${gh_pages_dir}" gh-pages >/dev/null 2>&1; then echo "created worktree"; fi
rel_dir="$$(git rev-parse --show-prefix)"
echo "$${gh_pages_dir}"
endef
export BROWSER_GITSCRIPT
#BROWSER := python -c "$$BROWSER_PYSCRIPT"

gh_pages_docs = $(shell bash -c "$$BROWSER_GITSCRIPT")

html-publish: html
	@echo "$(gh_pages_docs)"
	cp -R build/html/* $(gh_pages_docs)
	cd $(gh_pages_docs); git add .; git commit -m"made with make"; git push

clean:
	rm -rf build/*

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
