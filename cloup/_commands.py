import abc
from typing import (
    Dict,
    Iterable,
    Optional,
    Type,
    cast,
)

import click

from ._option_groups import OptionGroupMixin
from ._sections import Section, SectionMixin
from .constraints import ConstraintMixin


class Command(ConstraintMixin, OptionGroupMixin, click.Command):
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

    def command(  # type: ignore
        self, name: Optional[str] = None,
        section: Optional[Section] = None,
        cls: Optional[Type[click.Command]] = None,
        **attrs,
    ):
        """Creates a new command and adds it to this group."""
        if cls is None:
            cls = Command

        def decorator(f):
            cmd = command(name=name, cls=cls, **attrs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    def group(  # type: ignore
        self, name: Optional[str] = None,
        section: Optional[Section] = None,
        cls: Optional[Type[click.Group]] = None,
        **attrs,
    ):
        if cls is None:
            cls = Group
        return self.command(name=name, section=section, cls=cls, **attrs)


def group(name: Optional[str] = None, cls: Type[click.Group] = Group, **attrs):
    """ Creates a new :class:`Group` using the decorated function as
    callback. This is just a convenience function equivalent to::

        click.group(name, cls=cloup.Group, **attrs)

    :param name: name of the command
    :param cls: type of Group
    :param attrs: any argument you can pass to :func:`click.group`
    """
    return cast(Group, click.group(name=name, cls=cls, **attrs))


def command(
    name: Optional[str] = None,
    cls: Type[click.Command] = Command,
    **attrs
):
    """
    Decorator that creates a new command using the wrapped function as callback.

    The only differences with respect to ``click.commands`` are:

    - this decorator creates a ``cloup.Command`` by default;
    - this decorator supports ``@constraint``.

    :param name: name of the command
    :param cls: type of click.Command
    :param attrs: any argument you can pass to :func:`click.command`
    """

    def wrapper(f):
        if hasattr(f, '__constraints'):
            if not issubclass(cls, ConstraintMixin):
                raise TypeError(
                    f"a Command must inherits from cloup.ConstraintMixin to support "
                    f"constraints; {cls} doesn't")
            constraints = tuple(reversed(f.__constraints))
            del f.__constraints
            attrs['constraints'] = constraints

        return click.command(name, cls=cls, **attrs)(f)

    return wrapper
