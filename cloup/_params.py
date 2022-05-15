import click


class Argument(click.Argument):
    def __init__(self, *args, help=None, **attrs):
        super().__init__(*args, **attrs)
        self.help = help

    def get_help_record(self, ctx):
        return (self.make_metavar(), self.help or "")


class Option(click.Option):
    """A click.Option with an extra field ``group`` of type ``OptionGroup``."""

    def __init__(self, *args, group=None, **attrs):
        super().__init__(*args, **attrs)
        self.group = group


GroupedOption = Option
"""Alias of ``Option``."""


def argument(*args, help=None, cls=Argument, **kwargs):
    return click.argument(*args, help=help, cls=cls, **kwargs)


def option(*param_decls, cls=None, group=None, **kwargs):
    """Attaches an ``Option`` to the command.
    Refer to :class:`click.Option` and :class:`click.Parameter` for more info
    about the accepted parameters.

    In your IDE, you won't see arguments that have to do with shell completion,
    because they are different in Click 7 and 8 (both supported by Cloup):

    - in Click 7, it's ``autocompletion``
    - in Click 8, it's ``shell_complete``.

    These arguments have different semantics, refer to Click's docs.
    """
    if cls is None:
        cls = Option

    def decorator(f):
        func = click.option(*param_decls, cls=cls, **kwargs)(f)
        new_option = func.__click_params__[-1]
        new_option.group = group
        if group and group.hidden:
            new_option.hidden = True
        return func

    return decorator
