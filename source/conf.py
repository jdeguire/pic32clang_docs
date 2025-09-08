# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# ----------------------------------------------------------------------------

project = 'LLVM For PIC32'
copyright = '2025, Jesse DeGuire'
author = 'Jesse DeGuire'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# ----------------------------------------------------------------------------

# The default is "index", but this name will be easier to see since it will be at the top of the
# directory listing.
master_doc = '__start_here__'

# These are extensions we want to use with Sphinx. MyST is a flavor of Markdown that has extensions 
# for technical writing. It has some similarities to GitHub Flavored Markdown. Sphinx comes with its
# own extensions, such as this one that lets us add "TODO" admonitions to our document.
extensions = ['myst_parser',
              'sphinx.ext.todo']

# MyST has its own extensions, which we can enable here.
myst_enable_extensions = ['attrs_inline']

# Yes, we want to see the "TODO" admonitions in the output.
todo_include_todos = True

# Automatically create references we can link to for headings up to 3 levels deep.
myst_heading_anchors = 3

# Default stuff.
templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# ----------------------------------------------------------------------------

# Theme and options for that theme
html_theme = 'classic'
html_theme_options = {
    'sidebarwidth': '250',
    'body_max_width': '1000'
}

# To link to external documents, we have to tell MyST how to find them. Otherwise, it will try to
# look relative to the source file, which isn't what we want. MyST handles http, https, mailto, and
# ftp by default, but if we want custom ones we need to specify them here. For example, in the document
# we could put 
# 
#   [linky](llvm:foo.html#bar)
#
# and the final link will resolve to "../share/doc/LLVM/foo.html#bar". This will be relative to wherever
# the built document is located.
myst_url_schemes = {
    'http': None,
    'https': None,
    'ftp': None,
    'mailto': None,
    'llvm': '../share/doc/LLVM/{{path}}#{{fragment}}',
    'runtimes': '../share/doc/Runtimes/{{path}}#{{fragment}}',
    'cmsis': '../CMSIS/Documentation/{{path}}#{{fragment}}'
}

# Default stuff.
html_static_path = ['_static']
