from collections import OrderedDict
from typing import Callable, Optional, Sequence, overload

import click


class OptionGroup:
    def __init__(self, name, help=None):  # noqa
        if not name:
            raise ValueError('name is a mandatory argument')
        self.name = name
        self.help = help
        self.options = []

    def get_help_records(self, ctx):
        return [opt.get_help_record(ctx) for opt in self if not opt.hidden]

    def option(self, *param_decls, **attrs):
        return option(*param_decls, group=self, **attrs)

    def __iter__(self):
        return iter(self.options)

    def __getitem__(self, i):
        return self.options[i]

    def __len__(self) -> int:
        return len(self.options)

    def __repr__(self):
        return 'OptionGroup({!r}, help={!r}, options={})'.format(
            self.name, self.help, self.options)

    def __str__(self):
        return 'OptionGroup({!r}, help={!r}, options={})'.format(
            self.name, self.help, [opt.name for opt in self.options])


class GroupedOption(click.Option):
    """ A click.Option with an extra field ``group`` of type OptionGroup """

    def __init__(self, param_decls=None, show_default=False, prompt=False,
                 confirmation_prompt=False, hide_input=False, is_flag=None, flag_value=None,
                 multiple=False, count=False, allow_from_autoenv=True, type=None, help=None,
                 hidden=False, show_choices=True, show_envvar=False, group=None, **attrs):
        self.group = group
        super().__init__(param_decls, show_default, prompt, confirmation_prompt, hide_input,
            is_flag, flag_value, multiple, count, allow_from_autoenv, type, help,
            hidden, show_choices, show_envvar, **attrs)


class GroupSection(object):
    """
    A section of commands inside a ``cloup.Group``. Sections are not
    (multi)commands, they simply allow to organize cloup.Group subcommands
    in many different help sections.
    """

    def __init__(self, title, commands=(), sorted=False):  # noqa
        """
        :param title:
        :param commands: list of commands, dictionary {name: command}
        :param sorted:
            if True, ``list_commands()`` returns the commands in lexicographic order
        """
        self.title = title
        self.sorted = sorted
        if isinstance(commands, (list, tuple)):
            self.commands = OrderedDict()
            for cmd in commands:
                self.add_command(cmd)
        else:
            try:
                self.commands = OrderedDict(commands)
            except TypeError:
                raise TypeError('commands must be a list of commands or a dict {name: command}')

    @classmethod
    def sorted(cls, title, commands=()):
        return cls(title, commands, sorted=True)

    def add_command(self, cmd, name=None):
        name = name or cmd.name
        if not name:
            raise TypeError('missing command name')
        if name in self.commands:
            raise Exception('command "{}" already exists'.format(name))
        self.commands[name] = cmd

    def list_commands(self):
        command_list = [(name, cmd) for name, cmd in self.commands.items() if not cmd.hidden]
        if self.sorted:
            command_list.sort()
        return command_list

    def __len__(self):
        return len(self.commands)

    def __repr__(self):
        return 'GroupSection({}, sorted={})'.format(self.title, self.sorted)


def has_option_group(param):
    return hasattr(param, 'group') and param.group is not None


def get_option_group_of(param, default=None):
    return param.group if has_option_group(param) else default


class Command(click.Command):
    """ A ``click.Command`` supporting option groups. """

    def __init__(self, name, context_settings=None, callback=None, params=None,
                 help=None, epilog=None, short_help=None, options_metavar='[OPTIONS]',
                 add_help_option=True, hidden=False, deprecated=False, align_option_groups=True):

        super().__init__(name, context_settings, callback, params, help, epilog, short_help,
            options_metavar, add_help_option, hidden, deprecated)

        options_by_group = OrderedDict()
        for param in self.params:
            if isinstance(param, click.Argument):
                continue
            options_by_group.setdefault(get_option_group_of(param), []).append(param)

        self.ungrouped_options = options_by_group.pop(None, default=[])
        self.option_groups = list(options_by_group.keys())
        for group, options in options_by_group.items():
            group.options = options
        self.align_option_groups = align_option_groups

    def get_ungrouped_options(self, ctx):
        help_option = self.get_help_option(ctx)
        if help_option is not None:
            return self.ungrouped_options + [help_option]
        else:
            return self.ungrouped_options

    def format_option_group(self, ctx, formatter, option_group, help_records=None):  # noqa
        help_records = help_records or option_group.get_help_records(ctx)
        if not help_records:
            return
        with formatter.section(option_group.name):
            if option_group.help:
                formatter.write_text(option_group.help)
            formatter.write_dl(help_records)

    def format_options(self, ctx, formatter, max_option_width=30):
        records_by_group = {group: group.get_help_records(ctx)
                            for group in self.option_groups}
        ungrouped_options = self.get_ungrouped_options(ctx)
        if ungrouped_options:
            default_group = OptionGroup('Other options' if records_by_group else 'Options')
            default_group.options = ungrouped_options
            records_by_group[default_group] = default_group.get_help_records(ctx)

        if self.align_option_groups:
            option_name_width = min(
                max_option_width,
                max(len(rec[0])
                    for records in records_by_group.values()
                    for rec in records)
            )
            # Pad the first column of the first entry of each group to reach option_name_width
            for records in records_by_group.values():
                first = records[0]
                pad_width = option_name_width - len(first[0])
                if pad_width <= 0:
                    continue
                records[0] = (first[0] + ' ' * pad_width, first[1])

        for group, records in records_by_group.items():
            self.format_option_group(ctx, formatter, group, help_records=records)


class Group(click.Group):
    """
    A ``click.Group``:

    #. whose ``command()`` and ``group()`` methods returns resp. a ``cloup.Command``
       and a ``cloup.Group``;
    #. that allows to group subcommands into "sections" in the help.

    Subgroups can be specified in different ways:

    #. just pass a list of GroupSection objects to the constructor in ``sections``
    #. use ``add_section`` to add a section
    #. use ``add_command(cmd, name, section, ...)``
    #. use ``group.command(name, section, ...)``

    Commands not included in any user-defined section are added to the
    "default section", whose title is "Commands" or "Other commands" depending
    on whether it is the only section or not. The default section is the last
    shown section in the help and its commands are listed in lexicographic order.
    """

    def __init__(self, name=None, commands=None, sections=(), align_sections=True, **attrs):
        """
        :param name: name of the command
        :param commands: dict {name: command}; this command will be added to the default section.
        :param sections: a list of GroupSection objects
        :param align_sections: if True, the help column of all columns will be aligned;
            if False, each section will be formatted independently
        :param attrs:
        """
        super().__init__(name, commands=commands, **attrs)
        self.align_sections = align_sections
        self._default_section = GroupSection(None, commands=commands or [])
        self._user_sections = []
        self._section_set = set([self._default_section])
        for section in sections:
            self.add_section(section)

    def command(self, name=None, section=None, cls=Command, **attrs):
        """ Creates a new command and adds it to this group. """

        def decorator(f):
            cmd = command(name=name, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    def group(self, name=None, section=None, cls=None, **attrs):
        if cls is None:
            cls = Group

        def decorator(f):
            cmd = group(name=name, cls=cls, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    def _add_command_to_section(self, cmd, name=None, section=None):
        """ Adds a command to the section (if specified) or to the default section """
        name = name or cmd.name
        if section is None:
            section = self._default_section
        section.add_command(cmd, name)
        if section not in self._section_set:
            self._user_sections.append(section)
            self._section_set.add(section)

    def add_section(self, section):
        """ Adds a :class:`GroupSection` to this group. You can add the same
        section object a single time. """
        if section in self._section_set:
            raise ValueError('section {} was already added'.format(section))
        self._user_sections.append(section)
        self._section_set.add(section)
        for name, cmd in section.commands.items():
            super().add_command(cmd, name)

    def section(self, title, *commands, **attrs):
        """ Creates a new :class:`GroupSection`, adds it to this group and returns it. """
        section = GroupSection(title, commands, **attrs)
        self.add_section(section)
        return section

    def add_command(self, cmd, name=None, section=None):
        """
        Adds a new command. If ``section`` is None, the command is added to the default section.
        """
        super().add_command(cmd, name)
        self._add_command_to_section(cmd, name, section)

    def list_sections(self, ctx, include_default_section=True):
        """ Returns the list of all sections in the "correct order".
         if ``include_default_section=True`` and the default section is non-empty,
         it will be included at the end of the list. """
        section_list = list(self._user_sections)
        if include_default_section and len(self._default_section) > 0:
            default_section = GroupSection.sorted(
                title='Other commands' if len(self._user_sections) > 0 else 'Commands',
                commands=self._default_section.commands)
            section_list.append(default_section)
        return section_list

    def format_commands(self, ctx, formatter):
        section_list = self.list_sections(ctx)
        command_name_col_width = None
        if self.align_sections:
            command_name_col_width = max(len(name)
                                         for section in section_list
                                         for name in section.commands)
        for section in section_list:
            self.format_section(ctx, formatter, section, command_name_col_width)

    def format_section(self, ctx, formatter, section, command_col_width=None):  # noqa
        commands = section.list_commands()
        if not commands:
            return

        if command_col_width is None:
            command_col_width = max(len(cmd_name) for cmd_name, _ in commands)

        limit = formatter.width - 6 - command_col_width
        rows = []
        for name, cmd in commands:
            short_help = cmd.get_short_help_str(limit)
            padded_name = name + ' ' * (command_col_width - len(name))
            rows.append((padded_name, short_help))

        if rows:
            with formatter.section(section.title):
                formatter.write_dl(rows)


def group(name=None, cls=Group, **attrs):
    """ Creates a new ``Group`` (by default). """
    return click.group(name=name, cls=cls, **attrs)


def command(name=None, cls=Command, **attrs):
    """ Creates a new ``cloup.Command`` (by default). """
    return click.command(name, cls=cls, **attrs)


def option(*param_decls, group=None, cls=GroupedOption, **attrs):
    def decorator(f):
        click.option(*param_decls, cls=cls, **attrs)(f)
        new_option = f.__click_params__[-1]
        new_option.group = group
        return f

    return decorator


@overload
def option_group(name: str, help: str, *options) -> Callable:  # noqa
    ...


@overload
def option_group(name: str, *options, help: Optional[str] = None) -> Callable:  # noqa
    ...


def option_group(name: str, *args, **kwargs):
    """
    Attaches an option group to the command. This decorator is overloaded with
    two signatures::

        @option_group(name: str, *options, help: Optional[str] = None)
        @option_group(name: str, help: str, *options)

    In other words, if the second position argument is a string, it is interpreted
    as the "help" argument. Otherwise, it is interpreted as the first option;
    in this case, you can still pass the help as keyword argument.
    """
    if isinstance(args[0], str):
        return _option_group(name, options=args[1:], help=args[0], **kwargs)
    else:
        return _option_group(name, options=args, **kwargs)


def _option_group(name: str,
                  options: Sequence[Callable],
                  help: Optional[str] = None) -> Callable:  # noqa
    if not options:
        raise ValueError('you must provide at least one option')

    opt_group = OptionGroup(name, help=help)

    def decorator(f):
        for opt_decorator in reversed(options):
            opt_decorator(f)
            new_option = f.__click_params__[-1]
            curr_group = get_option_group_of(new_option)
            if curr_group is not None:
                raise ValueError(
                    'option {} was first assigned to {} and then passed '
                    'as argument to @option_group({!r}, ...)'
                        .format(new_option.opts, curr_group, name))
            new_option.group = opt_group
        return f

    return decorator
