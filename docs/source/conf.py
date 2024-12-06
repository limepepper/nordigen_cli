# -- Project information -----------------------------------------------------

project = "Nordigen Cli"
copyright = "2024, Tom Hodder"
author = "Tom Hodder"
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx-pydantic",
    "sphinxcontrib.typer",
    "sphinx_inline_tabs",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_extra_path = ["extra"]


# def setup(app):
#     # Register a sphinx.ext.autodoc.between listener to ignore everything
#     # between lines that contain the word IGNORE
#     app.connect("autodoc-process-docstring", between("^.*IGNORE.*$", exclude=True))
#     return app
