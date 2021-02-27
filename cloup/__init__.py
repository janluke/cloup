"""Top-level package for cloup."""

__author__ = """Gianluca Gippetto"""
__email__ = 'gianluca.gippetto@gmail.com'
__version__ = '0.6.0'

# flake8: noqa F401
from ._option_groups import (
    GroupedOption, OptionGroup, OptionGroupMixin, option, option_group
)
from ._sections import Section, SectionMixin
from ._commands import Command, Group, MultiCommand, command, group
from .constraints import ConstraintMixin, constraint
