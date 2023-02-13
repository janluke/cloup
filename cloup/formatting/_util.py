import warnings
from typing import TYPE_CHECKING, cast

import click
from wcwidth import wcswidth

if TYPE_CHECKING:
    import cloup

FORMATTER_TYPE_ERROR = """
since Cloup v0.8, this class relies on `cloup.HelpFormatter` to align help
sections. So, you need to make sure your command class uses `cloup.HelpFormatter`
as formatter class.

If you have your own custom `HelpFormatter`, know that `cloup.HelpFormatter` is
more easily customizable then Click's one, so consider extending it instead
of extending `click.HelpFormatter`.
"""


def ensure_is_cloup_formatter(formatter: click.HelpFormatter) -> 'cloup.HelpFormatter':
    from cloup import HelpFormatter
    if isinstance(formatter, HelpFormatter):
        return formatter
    raise TypeError(FORMATTER_TYPE_ERROR)


def display_width(string: str) -> int:
    return cast(int, wcswidth(click.unstyle(string)))


def unstyled_len(string: str) -> int:
    warnings.warn(
        "`unstyled_len()` is deprecated; use `display_width()` instead",
        DeprecationWarning
    )
    return len(click.unstyle(string))
