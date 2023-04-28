"""Sphinx configuration file."""

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

import ark  # noqa: E402

project = "Ark"
copyright = f"2023, {ark.__author__}"
author = ark.__author__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

napoleon_google_docstring = True
napoleon_use_param = False
napoleon_use_ivar = True


html_theme = "sphinx_rtd_theme"
