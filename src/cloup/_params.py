"""This module contains Cloup parameter classes and decorators."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, TypeVar, overload

import click
from click.decorators import _param_memo
from click.shell_completion import CompletionItem

if sys.version_info >= (3, 12):
    from typing import TypedDict, Unpack
else:
    from typing_extensions import TypedDict, Unpack

from .typing import F

if TYPE_CHECKING:
    from ._option_groups import OptionGroup

P = TypeVar("P", bound=click.Parameter)

SimpleParamTypeLike = click.ParamType[Any] | Callable[[str], Any]
ParamTypeLike = SimpleParamTypeLike | tuple[SimpleParamTypeLike, ...]
ParamDefault = Any | Callable[[], Any]
ParamCallback = Callable[[click.Context, P, Any], Any]
ShellCompleteArg = Callable[
    [click.Context, P, str],
    list[CompletionItem] | list[str],
]


class _ParamKwargs(TypedDict, total=False):
    """Arguments accepted by both :func:`argument` and :func:`option`.

    Refer to :class:`click.Parameter` for their meaning and defaults.
    """

    help: str | None
    deprecated: bool | str
    type: ParamTypeLike | None
    required: bool | None
    default: ParamDefault | None
    nargs: int | None
    metavar: str | None
    expose_value: bool
    envvar: str | Sequence[str] | None


class ArgumentKwargs(_ParamKwargs, total=False):
    """Arguments accepted by :func:`argument`.

    Refer to :class:`click.Argument` for their meaning and defaults.
    """

    callback: ParamCallback[click.Argument] | None
    shell_complete: ShellCompleteArg[click.Argument] | None


class OptionKwargs(_ParamKwargs, total=False):
    """Arguments accepted by :func:`option`.

    Refer to :class:`click.Option` for their meaning and defaults.
    """

    callback: ParamCallback[click.Option] | None
    shell_complete: ShellCompleteArg[click.Option] | None
    # Commonly used
    is_flag: bool | None
    # Processing
    is_eager: bool
    # Help text tuning
    show_choices: bool
    show_default: bool | str | None
    show_envvar: bool
    # Flag options
    flag_value: Any
    count: bool
    # Multiple values
    multiple: bool
    # Prompt
    prompt: bool | str
    confirmation_prompt: bool | str
    prompt_required: bool
    hide_input: bool
    # Environment
    allow_from_autoenv: bool
    # Hiding
    hidden: bool


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


@overload
def argument(
    *param_decls: str,
    cls: None = None,
    **attrs: Unpack[ArgumentKwargs],
) -> Callable[[F], F]: ...


# A custom ``cls`` may accept arguments that cannot be known here, so this
# overload takes any keyword.
@overload
def argument(
    *param_decls: str,
    cls: type[click.Argument],
    **attrs: Any,
) -> Callable[[F], F]: ...


def argument(
    *param_decls: str,
    cls: type[click.Argument] | None = None,
    **attrs: Any,
) -> Callable[[F], F]:
    """Attach an ``Argument`` to the command.

    The accepted arguments are listed in :class:`cloup.ArgumentKwargs`; refer to
    :class:`click.Argument` and :class:`click.Parameter` for their meaning.
    """
    ArgumentClass = cls or click.Argument

    def decorator(f: F) -> F:
        _param_memo(f, ArgumentClass(param_decls, **attrs))
        return f

    return decorator


@overload
def option(
    *param_decls: str,
    cls: None = None,
    group: OptionGroup | None = None,
    **attrs: Unpack[OptionKwargs],
) -> Callable[[F], F]: ...


# A custom ``cls`` may accept arguments that cannot be known here, so this
# overload takes any keyword.
@overload
def option(
    *param_decls: str,
    cls: type[click.Option],
    group: OptionGroup | None = None,
    **attrs: Any,
) -> Callable[[F], F]: ...


def option(
    *param_decls: str,
    cls: type[click.Option] | None = None,
    group: OptionGroup | None = None,
    **attrs: Any,
) -> Callable[[F], F]:
    """Attach an ``Option`` to the command.

    The accepted arguments are listed in :class:`cloup.OptionKwargs`; refer to
    :class:`click.Option` and :class:`click.Parameter` for their meaning.

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
