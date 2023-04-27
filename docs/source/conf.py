"""Sphinx configuration file."""

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

project = "Ark"
copyright = "2023, Anthony Pagan"
author = "Anthony Pagan"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

napoleon_google_docstring = True
napoleon_use_param = False
napoleon_use_ivar = True


html_theme = "sphinx_rtd_theme"