"""Top-level package for cloup."""

__author__ = """Gianluca Gippetto"""
__email__ = 'gianluca.gippetto@gmail.com'
__version__ = '0.3.0'

# flake8: noqa F401
from ._cloup import (
    OptionGroup,
    GroupSection,
    GroupedOption,
    Group,
    Command,
    option_group,
    option,
    command,
    group
)
