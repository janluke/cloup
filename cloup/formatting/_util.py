from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ._formatter import HelpFormatter

FORMATTER_TYPE_ERROR = """
since cloup v0.8.0, this class relies on cloup.HelpFormatter to align help
sections. So, you need to make sure your command class uses cloup.HelpFormatter
as formatter class.

If you have your own custom HelpFormatter, know that cloup.HelpFormatter is
more easily customizable then Click's one, so consider extending it instead
of extending click.HelpFormatter.
"""


def ensure_is_cloup_formatter(formatter: click.HelpFormatter) -> 'HelpFormatter':
    from cloup import HelpFormatter
    if isinstance(formatter, HelpFormatter):
        return formatter
    raise TypeError(FORMATTER_TYPE_ERROR)


def unstyled_len(string: str) -> int:
    return len(click.unstyle(string))
