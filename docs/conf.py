#!/usr/bin/env python

import os

import cloup


PROJ_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc.typehints',
    'autoapi.extension',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_panels',
    'sphinx_copybutton',  # adds a copy button to code blocks
    'versionwarning.extension',
    'sphinx_issues',  # link to GitHub issues and PRs
]

# General information about the project.
project = 'cloup'
copyright = "2020, Gianluca Gippetto"
author = "Gianluca Gippetto"
issues_github_path = "janLuke/cloup"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|.
_version = tuple(map(str, cloup.__version_tuple__))
version = '.'.join(_version[:4])
release = '.'.join(_version)

language = "en"

# Autodoc
autoclass_content = 'both'
autodoc_typehints = 'description'
set_type_checking_flag = True
typehints_fully_qualified = False

# Autoapi
autoapi_type = 'python'
autoapi_dirs = [os.path.join(PROJ_DIR, 'cloup')]
autoapi_template_dir = '_autoapi_templates'
templates_path = [autoapi_template_dir]
autoapi_keep_files = True
autoapi_add_toctree_entry = False
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'special-members',
    'imported-members',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/', None),
    'Click': ('https://click.palletsprojects.com', None)
}

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = '.rst'
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output ---------------------------------------------------
html_title = f"Cloup v{version}: option groups for Click"
html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/janluke/cloup",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "home_page_in_toc": True,
    "extra_navbar": None,
}
pygments_style = 'default'  # name of the Pygments (syntax highlighting) style

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

def primary_color_with_alpha(alpha):
    return "rgba(0, 113, 188, %f)" % alpha

panels_css_variables = {
    "tabs-color-label-active": primary_color_with_alpha(1.0),
    "tabs-color-label-inactive": primary_color_with_alpha(0.5),
    "tabs-color-overline": primary_color_with_alpha(0.2),
    # "tabs-color-underline": "rgb(207, 236, 238)",
    # "tabs-size-label": "1rem",
}
panels_add_bootstrap_css = False
html_css_files = [
    'styles/copybutton-overrides.css',
    'styles/tabs-overrides.css',
    'styles/theme-overrides.css',
]

# -- Version warning -----------------------------------------------------------
versionwarning_messages = {
    "latest": (
        "this document is for the development version. "
        'For the stable version documentation, see <a href="/en/stable/">here</a>.'
    ),
}
# versionwarning_project_version = "latest"    # For debugging locally
versionwarning_body_selector = "body"
versionwarning_banner_title = ""
versionwarning_banner_html = """
<div id="{id_div}">
    <strong>Warning:</strong> {message}
</div>
"""

# Whether to render to-do notes.
todo_include_todos = False

# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'cloupdoc'

# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'cloup.tex',
     'cloup Documentation',
     'Gianluca Gippetto', 'manual'),
]

# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'cloup',
     'cloup Documentation',
     [author], 1)
]
