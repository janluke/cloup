from collections import OrderedDict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, Union

import click

CommandType = TypeVar('CommandType', bound=Type[click.Command])
Subcommands = Union[Iterable[click.Command], Dict[str, click.Command]]


class Section:
    """
    A group of (sub)commands to show in the same help section of a
    ``MultiCommand``. You can use sections with any `Command` that inherits
    from :class:`SectionMixin`.

    .. versionchanged:: 0.6.0
        Removed the deprecated old name ``GroupSection``.

    .. versionchanged:: 0.5.0
        Introduced the new name ``Section`` and deprecated the old ``GroupSection``.
    """

    def __init__(self, title: str,
                 commands: Subcommands = (),
                 sorted: bool = False):  # noqa
        """
        :param title:
        :param commands: sequence of commands or dictionary {name: command}
        :param sorted:
            if True, ``list_commands()`` returns the commands in lexicographic order
        """
        self.title = title
        self.sorted = sorted  # type: ignore
        self.commands: OrderedDict[str, click.Command] = OrderedDict()
        if isinstance(commands, Sequence):
            self.commands = OrderedDict()
            for cmd in commands:
                self.add_command(cmd)
        elif isinstance(commands, dict):
            self.commands = OrderedDict(commands)
        else:
            raise TypeError('the argument "commands" must be a list of commands '
                            'or a dict {name: command}')

    @classmethod
    def sorted(cls, title: str, commands: Subcommands = ()) -> 'Section':
        return cls(title, commands, sorted=True)

    def add_command(self, cmd: click.Command, name: Optional[str] = None):
        name = name or cmd.name
        if not name:
            raise TypeError('missing command name')
        if name in self.commands:
            raise Exception('command "{}" already exists'.format(name))
        self.commands[name] = cmd

    def list_commands(self) -> List[Tuple[str, click.Command]]:
        command_list = [(name, cmd) for name, cmd in self.commands.items()
                        if not cmd.hidden]
        if self.sorted:
            command_list.sort()
        return command_list

    def __len__(self) -> int:
        return len(self.commands)

    def __repr__(self) -> str:
        return 'Section({}, sorted={})'.format(self.title, self.sorted)


class SectionMixin:
    """
    Adds to a click.MultiCommand the possibility to organize its subcommands
    in multiple help sections.

    Sections can be specified in the following ways:

    #. passing a list of :class:`Section` objects to the constructor setting
       the argument ``sections``
    #. using :meth:`add_section` to add a single section
    #. using :meth:`add_command` with the argument `section` set

    Commands not assigned to any user-defined section are added to the
    "default section", whose title is "Commands" or "Other commands" depending
    on whether it is the only section or not. The default section is the last
    shown section in the help and its commands are listed in lexicographic order.

    .. versionadded:: 0.5.0
    """

    def __init__(
        self, *args,
        commands: Optional[Dict[str, click.Command]] = None,
        sections: Iterable[Section] = (),
        align_sections: bool = True,
        **kwargs,
    ):
        """
        :param sections: a list of :class:`Section` objects
        :param align_sections: if True, the help column of all columns will be aligned;
            if False, each section will be formatted independently
        """
        self.align_sections = align_sections
        self._default_section = Section('__DEFAULT', commands=commands or [])
        self._user_sections: List[Section] = []
        self._section_set = {self._default_section}
        for section in sections:
            self.add_section(section)
        super().__init__(*args, commands=commands, **kwargs)  # type: ignore

    def _add_command_to_section(self, cmd, name=None, section=None):
        """ Adds a command to the section (if specified) or to the default section """
        name = name or cmd.name
        if section is None:
            section = self._default_section
        section.add_command(cmd, name)
        if section not in self._section_set:
            self._user_sections.append(section)
            self._section_set.add(section)

    def add_section(self, section: Section):
        """ Adds a :class:`Section` to this group. You can add the same
        section object a single time. """
        if section in self._section_set:
            raise ValueError('section {} was already added'.format(section))
        self._user_sections.append(section)
        self._section_set.add(section)
        for name, cmd in section.commands.items():
            super().add_command(cmd, name)  # type: ignore

    def section(self, title: str, *commands: click.Command, **attrs) -> Section:
        """ Creates a new :class:`Section`, adds it to this group and returns it. """
        section = Section(title, commands, **attrs)
        self.add_section(section)
        return section

    def add_command(self, cmd: click.Command,
                    name: Optional[str] = None,
                    section: Optional[Section] = None):
        """Adds a new command. If ``section`` is None, the command is added to
        the default section."""
        super().add_command(cmd, name)  # type: ignore
        self._add_command_to_section(cmd, name, section)

    def list_sections(self, ctx: click.Context,
                      include_default_section: bool = True) -> List[Section]:
        """ Returns the list of all sections in the "correct order".
         if ``include_default_section=True`` and the default section is non-empty,
         it will be included at the end of the list. """
        section_list = list(self._user_sections)
        if include_default_section and len(self._default_section) > 0:
            default_section = Section.sorted(
                title='Other commands' if len(self._user_sections) > 0 else 'Commands',
                commands=self._default_section.commands)
            section_list.append(default_section)
        return section_list

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter):
        section_list = self.list_sections(ctx)
        command_name_col_width = None
        if self.align_sections:
            command_name_col_width = max(len(name)
                                         for section in section_list
                                         for name in section.commands)
        for section in section_list:
            self.format_section(ctx, formatter, section, command_name_col_width)

    def format_section(self, ctx: click.Context,
                       formatter: click.HelpFormatter,
                       section: Section,
                       command_col_width: Optional[int] = None):
        commands = section.list_commands()
        if not commands:
            return

        if command_col_width is None:
            command_col_width = max(len(cmd_name) for cmd_name, _ in commands)

        limit = formatter.width - 6 - command_col_width  # type: ignore
        rows = []
        for name, cmd in commands:
            short_help = cmd.get_short_help_str(limit)
            padded_name = name + ' ' * (command_col_width - len(name))
            rows.append((padded_name, short_help))

        if rows:
            with formatter.section(section.title):
                formatter.write_dl(rows)
