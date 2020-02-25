from collections import OrderedDict
from functools import wraps

import click


class OptionGroup(object):
    def __init__(self, name, help=None):
        if not name:
            raise ValueError('name is a mandatory argument')
        self.name = name
        self.help = help

    def __repr__(self):
        return 'OptionGroup(name={}, help={})'.format(self.name, self.help)


class GroupedOption(click.Option):
    """ A click.Option with a an extra field ``group`` of type OptionGroup """

    def __init__(self, param_decls=None, show_default=False, prompt=False,
                 confirmation_prompt=False, hide_input=False, is_flag=None, flag_value=None,
                 multiple=False, count=False, allow_from_autoenv=True, type=None, help=None,
                 hidden=False, show_choices=True, show_envvar=False, group=None, **attrs):
        self.group = group
        super().__init__(param_decls, show_default, prompt, confirmation_prompt, hide_input,
                         is_flag, flag_value, multiple, count, allow_from_autoenv, type, help,
                         hidden, show_choices, show_envvar, **attrs)


class CloupCommand(click.Command):
    """ A ``click.Command`` supporting option groups. """

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        default_option_group = []
        opts_by_group = OrderedDict()
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if hasattr(param, 'group') and param.group:
                    opts_by_group.setdefault(param.group, []).append(rv)
                else:
                    default_option_group.append(rv)

        for option_group, entries in opts_by_group.items():
            with formatter.section(option_group.name):
                if option_group.help:
                    formatter.write_text(option_group.help)
                formatter.write_dl(entries)

        with formatter.section('Other options' if opts_by_group else 'Options'):
            formatter.write_dl(default_option_group)


class CloupGroup(click.Group):
    """ A ``click.Group`` supporting option groups. """
    def command(self, name=None, cls=CloupCommand, **attrs):
        return super().command(name=name, cls=cls, **attrs)

    def group(self, name=None, cls=None, **attrs):
        if cls is None:
            cls = CloupGroup
        return super().group(name=name, cls=cls, **attrs)


@wraps(click.group)
def group(name=None, **attrs):
    """ Creates a new ``CloupGroup``, i.e. a group supporting option groups. """
    return click.group(name=name, cls=CloupGroup, **attrs)


@wraps(click.command)
def command(name=None, cls=CloupCommand, **attrs):
    """ Creates a new ``CloupCommand``, i.e. a command supporting option groups. """
    return click.command(name, cls=cls, **attrs)


def option(*param_decls, **attrs):
    """ Attaches a ``GroupedOption``, i.e. an option supporting option groups. """
    def decorator(f, group=None):
        return click.option(*param_decls, cls=GroupedOption, group=group, **attrs)(f)

    return decorator


def option_group(name, options, help=None):
    """ Attaches an option group to the command. """
    group = OptionGroup(name, help)

    def decorator(f):
        composition = f
        for opt in reversed(options):
            composition = opt(composition, group)
        return composition

    return decorator
