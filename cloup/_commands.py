from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Type, cast

import click

from ._context import Context
from ._option_groups import OptionGroupMixin
from ._sections import Section, SectionMixin
from .constraints import BoundConstraintSpec, ConstraintMixin


class BaseCommand(click.Command):
    """Base class for cloup commands.

    * It back-ports a feature from Click v8.0-a1, i.e. the ``context_class``
      class attribute, which is set to ``cloup.Context``.

    * It adds a ``formatter_settings`` instance attribute.

    .. versionadded:: 0.8.0
    """
    context_class: Type[Context] = Context

    def __init__(
        self, *args,
        formatter_settings: Dict[str, Any] = {},
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        #: HelpFormatter options that are merged with ``Context.formatter_settings``
        #: (eventually overriding some values).
        self.formatter_settings = formatter_settings

    def make_context(self, info_name, args, parent=None, **extra) -> Context:
        for key, value in self.context_settings.items():
            if key not in extra:
                extra[key] = value

        ctx = self.context_class(self, info_name=info_name, parent=parent, **extra)

        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)
        return ctx

    # Differently from Click, this doesn't indent the epilog.
    def format_epilog(self, ctx, formatter):
        if self.epilog:
            formatter.write_paragraph()
            formatter.write_epilog(self.epilog)

    def format_help_text(self, ctx, formatter):
        formatter.write_command_help_text(self)


class Command(ConstraintMixin, OptionGroupMixin, BaseCommand):
    """
    A ``click.Command`` supporting option groups and constraints.

    .. versionchanged:: 0.8.0
        this class now inherits from :class:`cloup.BaseCommand`.
    """

    def __init__(
        self, *click_args,
        formatter_settings: Dict[str, Any] = {},
        constraints: Sequence[BoundConstraintSpec] = (),
        show_constraints: Optional[bool] = None,
        align_option_groups: Optional[bool] = None,
        **click_kwargs,
    ):
        super().__init__(
            *click_args,
            formatter_settings=formatter_settings,
            constraints=constraints,
            show_constraints=show_constraints,
            align_option_groups=align_option_groups,
            **click_kwargs)


class Group(SectionMixin, BaseCommand, click.Group):
    """
    A ``click.Group`` that allows to organize its subcommands in multiple help
    sections and and whose subcommands are, by default, of type
    :class:`cloup.Command`.

    This class is just a :class:`click.Group` mixed with :class:`SectionMixin`
    that overrides the decorators :meth:`command` and :meth:`group` so that
    a ``section`` for the created subcommand can be specified.

    See the docstring of the two superclasses for more details.

    .. versionchanged:: 0.8.0
        this class now inherits from :class:`cloup.BaseCommand`.
    """

    def __init__(self, name: Optional[str] = None,
                 commands: Optional[Dict[str, click.Command]] = None,
                 sections: Iterable[Section] = (),
                 align_sections: Optional[bool] = None,
                 formatter_settings: Dict[str, Any] = {},
                 **attrs):
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
            formatter_settings=formatter_settings,
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
        """Decorator for creating a new subcommand of this ``Group``.
        It takes the same arguments of :func:`command` plus ``section``."""
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
        """Decorator for creating a new subgroup of this command.
        It takes the same argument of :func:`group` plus ``section``."""
        if cls is None:
            cls = Group
        return self.command(name=name, section=section, cls=cls, **kwargs)


def group(
    name: Optional[str] = None,
    *,
    cls: Type[Group] = Group,
    sections: Iterable[Section] = (),
    align_sections: Optional[bool] = None,
    invoke_without_command: bool = False,
    no_args_is_help: bool = False,
    context_settings: Optional[Dict[str, Any]] = None,
    formatter_settings: Dict[str, Any] = {},
    help: Optional[str] = None,
    epilog: Optional[str] = None,
    short_help: Optional[str] = None,
    options_metavar: Optional[str] = "[OPTIONS]",
    subcommand_metavar: Optional[str] = None,
    add_help_option: bool = True,
    chain: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    **kwargs
) -> Callable[[Callable], Group]:
    """Decorator for creating a new :class:`cloup.Group` (or a subclass of it).

    :param name:
        the name of the command to use unless a group overrides it.
    :param cls:
        the ``cloup.Group`` (sub)class to instantiate.
    :param sections:
        a list of Section objects.
    :param align_sections:
        if ``True``, the help column of all columns will be aligned;
        if ``False``, each section will be formatted independently.
    :param context_settings:
        an optional dictionary with defaults that are passed to the context object.
    :param formatter_settings:
        arguments for the formatter; you can use :meth:`HelpFormatter.settings`
        to build this dictionary.
    :param help:
        the help string to use for this command.
    :param epilog:
        like the help string but it's printed at the end of the help page after
        everything else.
    :param short_help:
        the short help to use for this command.  This is shown on the command
        listing of the parent command.
    :param options_metavar:
        metavar for options shown in the command's usage string.
    :param add_help_option:
        by default each command registers a ``--help`` option.
        This can be disabled by this parameter.
    :param no_args_is_help:
        this controls what happens if no arguments are provided. This option is
        disabled by default. If enabled this will add ``--help`` as argument if
        no arguments are passed
    :param hidden:
        hide this command from help outputs.
    :param deprecated:
        issues a message indicating that the command is deprecated.
    :param invoke_without_command:
        this controls how the multi command itself is invoked. By default it's
        only invoked if a subcommand is provided.
    :param no_args_is_help:
        this controls what happens if no arguments are provided. This option is
        enabled by default if `invoke_without_command` is disabled or disabled
        if it's enabled. If enabled this will add ``--help`` as argument if no
        arguments are passed.
    :param subcommand_metavar:
        string used in the command's usage string to indicate the subcommand place.
    :param chain:
        if this is set to `True` chaining of multiple subcommands is enabled.
        This restricts the form of commands in that they cannot have optional
        arguments but it allows multiple commands to be chained together.
    :param kwargs:
        any other argument accepted by the instantiated command class.
    """
    if not issubclass(cls, Group):
        raise TypeError(
            'this decorator requires cls to be a cloup.Group or a subclass of it. '
            'Use @click.group to instantiate another type of Group but remember '
            'that some of the arguments of this decorator are only supported by '
            'cloup.Group.')

    kwargs.update(locals())
    kwargs.pop('kwargs')
    return cast(Callable[[Callable], Group], click.group(**kwargs))


def command(
    name: Optional[str] = None,
    *,
    cls: Type[click.Command] = Command,
    context_settings: Optional[Dict[str, Any]] = None,
    help: Optional[str] = None,
    epilog: Optional[str] = None,
    short_help: Optional[str] = None,
    options_metavar: Optional[str] = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    **kwargs
) -> Callable[[Callable], click.Command]:
    """
    Decorator that creates a new command using the decorated function as callback.

    The only differences with respect to ``click.commands`` are:

    - the default command class is :class:`cloup.Command`
    - supports ``@constraint`` (provided that ``cls=cloup.Command``).

    Besides of all the arguments documented below, you can pass any argument
    accepted by the instantiated command class (``cls``), which in the case of
    the default (:class:`cloup.Command`) include:

    - ``formatter_settings (dict)`` -- arguments for the formatter; you can use
      :meth:`HelpFormatter.settings` to build this dictionary.
    - ``align_option_groups (Optional[bool])``
    - ``show_constraints (Optional[bool])``.

    :param name:
        the name of the command to use unless a group overrides it.
    :param cls:
        the command class to instantiate.
    :param context_settings:
        an optional dictionary with defaults that are passed to the context object.
    :param help:
        the help string to use for this command.
    :param epilog:
        like the help string but it's printed at the end of the help page after
        everything else.
    :param short_help:
        the short help to use for this command.  This is shown on the command
        listing of the parent command.
    :param options_metavar:
        metavar for options shown in the command's usage string.
    :param add_help_option:
        by default each command registers a ``--help`` option.
        This can be disabled by this parameter.
    :param no_args_is_help:
        this controls what happens if no arguments are provided. This option is
        disabled by default. If enabled this will add ``--help`` as argument if
        no arguments are passed
    :param hidden:
        hide this command from help outputs.
    :param deprecated:
        issues a message indicating that the command is deprecated.
    :param kwargs:
        any other argument accepted by the instantiated command class.
    """
    kwargs.update(locals())
    kwargs.pop('kwargs')

    def wrapper(f):
        if hasattr(f, '__constraints'):
            if not issubclass(cls, ConstraintMixin):
                raise TypeError(
                    f"a Command must inherits from cloup.ConstraintMixin to support "
                    f"constraints; {cls} doesn't")
            constraints = tuple(reversed(f.__constraints))
            del f.__constraints
            kwargs['constraints'] = constraints

        cmd = click.command(**kwargs)(f)
        return cast(click.Command, cmd)

    return wrapper
