from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import click
from click.decorators import _param_memo

from .typing import F

if TYPE_CHECKING:
    from ._option_groups import OptionGroup


class Option(click.Option):
    """A :class:`click.Option` with an extra field ``group`` of type ``OptionGroup``."""

    group: OptionGroup | None

    def __init__(
        self,
        *args: Any,
        group: OptionGroup | None = None,
        **attrs: Any,
    ) -> None:
        super().__init__(*args, **attrs)
        self.group = group


def argument(
    *param_decls: str,
    cls: type[click.Argument] | None = None,
    **attrs: Any,
) -> Callable[[F], F]:
    cls = cls or click.Argument

    def decorator(f: F) -> F:
        _param_memo(f, cls(param_decls, **attrs))
        return f

    return decorator


def option(
    *param_decls: str,
    cls: type[click.Option] | None = None,
    group: OptionGroup | None = None,
    **attrs: Any,
) -> Callable[[F], F]:
    """Attach an ``Option`` to the command.
    Refer to :class:`click.Option` and :class:`click.Parameter` for more info
    about the accepted parameters.

    The type hints include Click's ``shell_complete`` callback and the
    Cloup-specific ``group`` argument.
    """
    OptionClass = cls or Option

    def decorator(f: F) -> F:
        new_option = OptionClass(param_decls, **attrs)
        _param_memo(f, new_option)
        setattr(new_option, "group", group)
        if group and group.hidden:
            new_option.hidden = True
        return f

    return decorator
