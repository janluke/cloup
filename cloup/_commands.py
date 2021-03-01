import abc
from typing import Callable, Dict, Iterable, Optional, Type, cast

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
        :param commands:
            dict {name: command}; this command will be added to the default section.
        :param sections: a list of Section objects
        :param align_sections: if True, the help column of all columns will be aligned;
            if False, each section will be formatted independently
        :param attrs:
        """
        super().__init__(
            name=name, commands=commands,
            sections=sections, align_sections=align_sections,
            **attrs)

    # MyPy complaints because the signature is not compatible with the parent
    # method signature, which is command(*args, **kwargs). Since the parent
    # method is implemented calling click.command(name=None, cls=None, **attrs),
    # any call that works for parent should work for us.
    def command(  # type: ignore
        self, name: Optional[str] = None,
        cls: Optional[Type[click.Command]] = None,
        section: Optional[Section] = None,
        **kwargs,
    ) -> Callable[[Callable], click.Command]:
        """Creates a new command and adds it to this group."""
        if cls is None:
            cls = Command

        def decorator(f):
            cmd = command(name=name, cls=cls, **kwargs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    # MyPy complaints because the signature is not compatible with the parent
    # method signature, which is group(*args, **kwargs). The "real signature"
    # of the parent method is command(name=None, cls=None, **attrs), thus
    # any call that works for parent should work for us, since the order of
    # named arguments is the same.
    def group(  # type: ignore
        self, name: Optional[str] = None,
        cls: Optional[Type[click.Group]] = None,
        section: Optional[Section] = None,
        **kwargs,
    ):
        if cls is None:
            cls = Group
        return self.command(name=name, section=section, cls=cls, **kwargs)


def group(
    name: Optional[str] = None, cls: Type[Group] = Group, **attrs
) -> Callable[[Callable], Group]:
    """Decorator for creating a new :class:`Group`.

    .. note::
        If you use static type checking, note that the ``cls`` optional argument
        of this function must be of type ``cloup.Group``, not ``click.Group``.

    :param name: name of the command
    :param cls: type of ``cloup.Group``
    :param attrs: any argument you can pass to :func:`click.group`
    """
    return cast(Callable[[Callable], Group],
                click.group(name=name, cls=cls, **attrs))


def command(
    name: Optional[str] = None,
    cls: Type[click.Command] = Command,
    **attrs
) -> Callable[[Callable], click.Command]:
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

        cmd = click.command(name, cls=cls, **attrs)(f)
        return cast(click.Command, cmd)

    return wrapper
