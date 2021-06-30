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

extlinks = {
    "issue": ("https://github.com/janLuke/cloup/issues/%s", "issue "),
    "pr": ("https://github.com/janLuke/cloup/pull/%s", "pull request "),
}

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|.
_version = tuple(map(str, cloup.__version_tuple__))
version = '.'.join(_version[:2])
release = '.'.join(_version[:3])

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
autoapi_python_class_content = 'both'
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
html_title = f"cloup v{version}"
html_theme = "furo"
html_theme_options = {
    "light_logo": "logo.svg",
    "dark_logo": "logo-dark-mode.svg",
    "sidebar_hide_name": True,
}
html_css_files = [
    'styles/extensions-overrides.css',
    'styles/theme-overrides.css',
]
pygments_style = 'default'  # name of the Pygments (syntax highlighting) style

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

primary_color = "#0094ff"
darker_primary_color = "#007bd3"
def primary_color_alpha(alpha):
    return "#2a5adf" + "{:02x}".format(int(alpha * 255))

panels_css_variables = {
    "tabs-color-label-active": darker_primary_color,
    "tabs-color-label-inactive": "var(--color-foreground-muted)",
    "tabs-color-overline": "var(--tabs--border)",
    "tabs-color-underline": "var(--tabs--border)",
}
panels_add_bootstrap_css = False


# -- Version warning -----------------------------------------------------------
versionwarning_messages = {
    "latest": (
        'This is the documentation for the main development branch of Cloup. '
        'The documentation for the latest stable release is '
        '<a href="/en/stable/">here</a>.'
    ),
}
# versionwarning_project_version = "latest"    # For debugging locally
versionwarning_body_selector = 'article[role="main"]'

# Whether to render to-do notes.
todo_include_todos = False

# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'cloupdoc'

# -- Options for LaTeX output ------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'cloup.tex',
     'cloup Documentation',
     'Gianluca Gippetto', 'manual'),
]
