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

from ._option_groups import OptionGroupMixin
from ._sections import Section, SectionMixin


class Command(OptionGroupMixin, click.Command):
    """
    A ``click.Command`` supporting option groups.
    This class is obtained by mixing :class:`click.Command` with
    :class:`cloup.OptionGroupMixin`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MultiCommand(SectionMixin, click.MultiCommand, metaclass=abc.ABCMeta):
    """
    A ``click.MultiCommand`` that allows to organize its subcommands in
    multiple help sections and and whose subcommands are, by default, of type
    :class:`cloup.Command`.

    This class is just a :class:`click.MultiCommand` mixed with
    :class:`SectionMixin`. See the docstring of the two superclasses for more
    details.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Group(SectionMixin, click.Group):
    """
    A ``click.Group`` that allows to organize its subcommands in multiple help
    sections and and whose subcommands are, by default, of type
    :class:`cloup.Command`.

    This class is just a :class:`click.Group` mixed with :class:`SectionMixin`
    that overrides the decorators :meth:`command` and :meth:`group` so that
    a ``section`` for the created subcommand can be specified.

    See the docstring of the two superclasses for more details.
    """

    def __init__(self, name: Optional[str] = None,
                 commands: Optional[Dict[str, click.Command]] = None,
                 sections: Iterable[Section] = (),
                 align_sections: bool = True, **attrs):
        """
        :param name: name of the command
        :param commands: dict {name: command}; this command will be added to the default section.
        :param sections: a list of Section objects
        :param align_sections: if True, the help column of all columns will be aligned;
            if False, each section will be formatted independently
        :param attrs:
        """
        super().__init__(
            name=name, commands=commands,
            sections=sections, align_sections=align_sections,
            **attrs)

    def command(self, name: Optional[str] = None,  # type: ignore
                section: Optional[Section] = None,
                cls: Type[click.Command] = Command, **attrs) -> Callable[[Callable], click.Command]:
        """ Creates a new command and adds it to this group. """

        def decorator(f):
            cmd = click.command(name=name, cls=cls, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    def group(self, name: Optional[str] = None,  # type: ignore
              section: Optional[Section] = None,
              cls: Optional[Type[click.Group]] = None,
              **attrs) -> Callable[[Callable], click.Group]:
        if cls is None:
            cls = Group

        def decorator(f):
            cmd = click.group(name=name, cls=cls, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator


def group(name: Optional[str] = None, **attrs) -> Callable[[Callable], Group]:
    """ Creates a new :class:`Group` using the decorated function as
    callback. This is just a convenience function equivalent to::

        click.group(name, cls=cloup.Group, **attrs)

    :param name: name of the command
    :param attrs: any argument you can pass to :func:`click.group`
    """
    return cast(Group, click.group(name=name, cls=Group, **attrs))


def command(name: Optional[str] = None, **attrs) -> Callable[[Callable], Command]:
    """
    Creates a new :class:`Command` using the decorated function as
    callback. This is just a convenience function equivalent to::

        click.command(name, cls=cloup.Command, **attrs)

    :param name: name of the command
    :param attrs: any argument you can pass to :func:`click.command`
    """
    return cast(Command, click.command(name, cls=Command, **attrs))
