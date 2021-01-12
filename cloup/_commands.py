import abc
from typing import (
    Callable,
    Dict,
    Iterable,
    Optional,
    Type,
    cast,
)

import click

from cloup import GroupSection, OptionGroupMixin, SectionMixin


class Command(OptionGroupMixin, click.Command):
    """
    A ``click.Command`` supporting option groups.
    This class is obtained by mixing :class:`click.Command` with
    :class:`cloup.OptionGroupMixin`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Group(click.Group):
    """
    A ``click.Group`` that allows to organize its subcommands in multiple help
    sections and and whose subcommands are, by default, of type :class:`cloup.Command`.

    This class is just a :class:`click.Group` mixed with :class:`cloup.SectionMixin`.
    See the docstring of these two subclasses for more details.
    """

    def __init__(self, name: Optional[str] = None,
                 commands: Optional[Dict[str, click.Command]] = None,
                 sections: Iterable[GroupSection] = (),
                 align_sections: bool = True, **attrs):
        """
        :param name: name of the command
        :param commands: dict {name: command}; this command will be added to the default section.
        :param sections: a list of GroupSection objects
        :param align_sections: if True, the help column of all columns will be aligned;
            if False, each section will be formatted independently
        :param attrs:
        """
        super().__init__(
            name=name, commands=commands,
            sections=sections, align_sections=align_sections,
            **attrs)

    def command(self, name: Optional[str] = None,  # type: ignore
                section: Optional[GroupSection] = None,
                cls: Type[click.Command] = Command, **attrs) -> Callable[[Callable], click.Command]:
        """ Creates a new command and adds it to this group. """

        def decorator(f):
            cmd = click.command(name=name, cls=cls, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    def group(self, name: Optional[str] = None,  # type: ignore
              section: Optional[GroupSection] = None,
              cls: Optional[Type[click.Group]] = None,
              **attrs) -> Callable[[Callable], click.Group]:
        if cls is None:
            cls = Group

        def decorator(f):
            cmd = click.group(name=name, cls=cls, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator


def group(name: Optional[str] = None,
          cls: Type[Group] = Group, **attrs) -> Callable[[Callable], Group]:
    """ Creates a new ``Group`` (by default). """
    if not issubclass(cls, Group):
        raise TypeError('cls must be a subclass of cloup.Group')
    return cast(Group, click.group(name=name, cls=cls, **attrs))


def command(name: Optional[str] = None,
            cls: Type[Command] = Command, **attrs) -> Callable[[Callable], Command]:
    """ Creates a new ``cloup.Command`` (by default). """
    if not issubclass(cls, Command):
        raise TypeError('cls must be a subclass of cloup.Command')
    return cast(Command, click.command(name, cls=cls, **attrs))
