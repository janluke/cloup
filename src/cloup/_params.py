from __future__ import annotations

from typing import TYPE_CHECKING

import click
from click.decorators import _param_memo

if TYPE_CHECKING:
    from ._option_groups import OptionGroup


class Option(click.Option):
    """A :class:`click.Option` with an extra field ``group`` of type ``OptionGroup``."""

    group: OptionGroup | None

    def __init__(self, *args, group=None, **attrs):
        super().__init__(*args, **attrs)
        self.group = group


GroupedOption = Option
"""Alias of ``Option``."""


def argument(*param_decls, cls=None, **attrs):
    cls = cls or click.Argument

    def decorator(f):
        _param_memo(f, cls(param_decls, **attrs))
        return f

    return decorator


def option(*param_decls, cls=None, group=None, **attrs):
    """Attach an ``Option`` to the command.
    Refer to :class:`click.Option` and :class:`click.Parameter` for more info
    about the accepted parameters.

    The type hints include Click's ``shell_complete`` callback and the
    Cloup-specific ``group`` argument.
    """
    OptionClass = cls or Option

    def decorator(f):
        _param_memo(f, OptionClass(param_decls, **attrs))
        new_option = f.__click_params__[-1]
        new_option.group = group
        if group and group.hidden:
            new_option.hidden = True
        return f

    return decorator
