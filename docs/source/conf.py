import os
import sys

# Add the project's root directory to the sys.path
sys.path.insert(0, os.path.abspath('..'))  # Adjust the path accordingly

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project: str = 'DCCEX_py'
copyright: str = '2025, Kaiden'
author: str = 'Kaiden Richardson'
release: str = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    'sphinx_markdown_builder',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    'sphinx.ext.viewcode'
]

autosummary_generate: bool = True

autodoc_default_options: dict[str, bool] = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'inherited-members': False,
    'show-inheritance': True,
}

templates_path: list[str] = ['_templates']
exclude_patterns: list[str] = []

pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme: str = 'alabaster'
html_static_path: list[str] = ['_static']
