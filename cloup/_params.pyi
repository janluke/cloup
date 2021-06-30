"""
Types for parameter decorators are in this stub for convenience of implementation.
"""
from typing import Any, Callable, Optional, Sequence, Type, TypeVar, Union

import click

from cloup import OptionGroup

F = TypeVar('F', bound=Callable)
P = TypeVar('P', bound=click.Parameter)

ParamTypeLike = Union[
    click.ParamType,
    Type[float], Type[int],
    Type[str], Type[tuple],
]
ParamDefault = Union[Any, Callable[[], Any]]
ParamCallback = Callable[[click.Context, P, Any], Any]

# Click 8 deprecates the argument `autocompletion` and replaces it with the
# argument `shell_complete`, which has a different semantic.
# The following will be uncommented when Cloup drop support for Click 7:
#
# ShellComplete = Callable[
#     [click.Context, P, str],
#     Union[List['CompletionItem'], List[str]],
# ]


class GroupedOption(click.Option):
    def __init__(self, *args, group: Optional[OptionGroup] = None, **kwargs):
        ...


def argument(
    *param_decls,
    cls: Optional[Type[click.Argument]] = None,
    type: Optional[ParamTypeLike] = None,
    required: Optional[bool] = None,
    default: Optional[ParamDefault] = None,
    callback: Optional[ParamCallback[click.Argument]] = None,
    nargs: Optional[int] = None,
    metavar: Optional[str] = None,
    expose_value: bool = True,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    # The following will be added when Cloup drops support for Click 7:
    #     shell_complete: Optional[ShellComplete] = None,
    **kwargs
) -> Callable[[F], F]: ...


def option(
    *param_decls,
    cls: Optional[Type[click.Option]] = None,
    # Commonly used
    metavar: Optional[str] = None,
    type: Optional[ParamTypeLike] = None,
    is_flag: Optional[bool] = None,
    default: Optional[ParamDefault] = None,
    required: Optional[bool] = None,
    help: Optional[str] = None,
    # Processing
    callback: Optional[ParamCallback[click.Option]] = None,
    is_eager: bool = False,
    # Help text tuning
    show_choices: bool = True,
    show_default: bool = False,
    show_envvar: bool = False,
    # Flag options
    flag_value: Optional[Any] = None,
    count: bool = False,
    # Multiple values
    nargs: Optional[int] = None,
    multiple: bool = False,
    # Prompt
    prompt: Union[bool, str] = False,
    confirmation_prompt: Union[bool, str] = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    # Environment
    allow_from_autoenv: bool = True,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    # Hiding
    hidden: bool = False,
    expose_value: bool = True,
    # Others
    group: Optional[OptionGroup] = None,
    # The following will be added when Cloup drops support for Click 7:
    #     shell_complete: Optional[ShellComplete] = None,
    **kwargs
) -> Callable[[F], F]: ...
