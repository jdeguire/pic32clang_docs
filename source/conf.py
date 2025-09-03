# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Clang For PIC32'
copyright = '2025, Jesse DeGuire'
author = 'Jesse DeGuire'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

master_doc = '__start_here__'
extensions = ['myst_parser',
              'sphinx.ext.todo']

todo_include_todos = True
myst_heading_anchors = 3
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_theme_options = {
    'sidebarwidth': '250',
    'body_max_width': '1000'
}

html_static_path = ['_static']
