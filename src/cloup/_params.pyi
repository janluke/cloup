"""
Types for parameter decorators are in this stub for convenience of implementation.
"""

from collections.abc import Callable, Sequence
from typing import (
    Any,
    TypeVar,
)

import click
from click.shell_completion import CompletionItem

from cloup import OptionGroup

F = TypeVar("F", bound=Callable[..., Any])
P = TypeVar("P", bound=click.Parameter)

SimpleParamTypeLike = click.ParamType[Any] | Callable[[str], Any]
ParamTypeLike = SimpleParamTypeLike | tuple[SimpleParamTypeLike, ...]
ParamDefault = Any | Callable[[], Any]
ParamCallback = Callable[[click.Context, P, Any], Any]
ShellCompleteArg = Callable[
    [click.Context, P, str],
    list[CompletionItem] | list[str],
]

class Option(click.Option):
    group: OptionGroup | None

    def __init__(self, *args: Any, group: OptionGroup | None = None, **attrs: Any): ...

def argument(
    *param_decls: str,
    cls: type[click.Argument] | None = None,
    help: str | None = None,
    deprecated: bool | str = False,
    type: ParamTypeLike | None = None,
    required: bool | None = None,
    default: ParamDefault | None = None,
    callback: ParamCallback[click.Argument] | None = None,
    nargs: int | None = None,
    metavar: str | None = None,
    expose_value: bool = True,
    envvar: str | Sequence[str] | None = None,
    shell_complete: ShellCompleteArg[click.Argument] | None = None,
    **kwargs: Any,
) -> Callable[[F], F]: ...
def option(
    *param_decls: str,
    cls: type[click.Option] | None = None,
    # Commonly used
    metavar: str | None = None,
    type: ParamTypeLike | None = None,
    is_flag: bool | None = None,
    default: ParamDefault | None = None,
    required: bool | None = None,
    help: str | None = None,
    deprecated: bool | str = False,
    # Processing
    callback: ParamCallback[click.Option] | None = None,
    is_eager: bool = False,
    # Help text tuning
    show_choices: bool = True,
    show_default: bool | str | None = None,
    show_envvar: bool = False,
    # Flag options
    flag_value: Any | None = None,
    count: bool = False,
    # Multiple values
    nargs: int | None = None,
    multiple: bool = False,
    # Prompt
    prompt: bool | str = False,
    confirmation_prompt: bool | str = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    # Environment
    allow_from_autoenv: bool = True,
    envvar: str | Sequence[str] | None = None,
    # Hiding
    hidden: bool = False,
    expose_value: bool = True,
    # Others
    group: OptionGroup | None = None,
    shell_complete: ShellCompleteArg[click.Option] | None = None,
    **kwargs: Any,
) -> Callable[[F], F]: ...
