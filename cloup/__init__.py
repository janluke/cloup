"""Top-level package for cloup."""

__author__ = """Gianluca Gippetto"""
__email__ = 'gianluca.gippetto@gmail.com'
__version__ = '0.4.1'

# flake8: noqa F401
from ._option_groups import (
    GroupedOption, OptionGroup, option, option_group,
)
from ._commands import (
    Command, Group, GroupSection, command, group,
)

