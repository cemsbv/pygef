# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "pygef"
copyright = "2020, Crux BV"
author = "Martina Pippi"

# The full version, including alpha/beta/rc tags
release = "0.4"

# 'sphinx.ext.napoleon' Used for numpy docstring support
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
exclude_patterns: list = []

html_theme = "nature"
