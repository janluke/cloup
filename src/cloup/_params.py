import inspect

import click
from click import Context
from click.decorators import _param_memo

from cloup._util import click_version_ge_8_5
from cloup.formatting._formatter import _format_deprecation_label

if click_version_ge_8_5:
    Argument = click.Argument
else:
    # Backport Click 8.5.0 feature

    class Argument(click.Argument):
        """A :class:`click.Argument` with help text."""

        def __init__(self, *args, help=None, deprecated=False, **attrs):
            super().__init__(*args, **attrs)

            if help:
                help = inspect.cleandoc(help)

            if deprecated:
                label = _format_deprecation_label(deprecated)
                help = f"{help} {label}" if help else label

            self.help = help
            self.deprecated = deprecated

        def make_metavar(self, ctx: Context) -> str:
            if self.metavar is not None:
                return self.metavar
            var = self.type.get_metavar(param=self, ctx=ctx)
            if not var:
                var = self.name.upper()
            # Types like ``Choice`` and ``DateTime`` already surround their metavar
            # with square brackets to enumerate the allowed values. Reuse those
            # outer brackets as the optional-argument indicator instead of wrapping
            # the metavar in a second pair, which would produce ``[[a|b|c]]``.
            already_bracketed = var.startswith("[") and var.endswith("]")
            if self.deprecated:
                var += "!"
            if not self.required and not already_bracketed:
                var = f"[{var}]"
            if self.nargs != 1:
                var += "..."
            return var


class Option(click.Option):
    """A :class:`click.Option` with an extra field ``group`` of type ``OptionGroup``."""

    def __init__(self, *args, group=None, **attrs):
        super().__init__(*args, **attrs)
        self.group = group


GroupedOption = Option
"""Alias of ``Option``."""


def argument(*param_decls, cls=None, **attrs):
    ArgumentClass = cls or Argument

    def decorator(f):
        _param_memo(f, ArgumentClass(param_decls, **attrs))
        return f

    return decorator


def option(*param_decls, cls=None, group=None, **attrs):
    """Attach an ``Option`` to the command.
    Refer to :class:`click.Option` and :class:`click.Parameter` for more info
    about the accepted parameters.

    In your IDE, you won't see arguments relating to shell completion,
    because they are different in Click 7 and 8 (both supported by Cloup):

    - in Click 7, it's ``autocompletion``
    - in Click 8, it's ``shell_complete``.

    These arguments have different semantics, refer to Click's docs.
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
