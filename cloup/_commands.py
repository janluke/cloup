"""
This modules contains command classes and decorators redefined by Cloup.

Note that Cloup commands *are* Click commands. Apart from supporting more features,
Cloup commands (and decorators) have detailed type hints. In particular, decorators
are generic and type checkers can precisely infer the type of the returned
command based on the ``cls`` argument!

Why did you overload all decorators?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To infer the return type based on the ``cls`` argument. Unfortunately, MyPy
doesn't allow to set a default value on a generic argument, see:
https://github.com/python/mypy/issues/3737.
So I had to resort to a workaround using @overload which makes things more
verbose:

- in one signature, ``cls`` has type ``None`` and it's set to ``None``; in this
  case I return the default ``cls``, which is ``cloup.Command`` for ``command``
  and ``cloup.Group`` for ``group
- in the other I use  ``cls: ClickCommand`` without a default, where ``ClickCommand``
  is a type variable.

When and if the MyPy issue is resolved, the overloads will be removed.
"""
from typing import (
    Any, Callable, Dict, Iterable, NamedTuple, Optional, Sequence, Type, TypeVar,
    overload,
)

import click

from ._context import Context
from ._option_groups import OptionGroupMixin
from ._sections import Section, SectionMixin
from ._util import reindent
from .constraints import ConstraintMixin

ClickCommand = TypeVar('ClickCommand', bound=click.Command)
ClickGroup = TypeVar('ClickGroup', bound=click.Group)


class BaseCommand(click.Command):
    """Base class for cloup commands.

    * It back-ports a feature from Click v8.0, i.e. the ``context_class``
      class attribute, which is set to ``cloup.Context``.

    * It adds a ``formatter_settings`` instance attribute.

    Refer to :class:`click.Command` for the documentation of all parameters.

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

    Refer to superclasses for the documentation of all accepted parameters:

    - :class:`ConstraintMixin`
    - :class:`OptionGroupMixin`
    - :class:`BaseCommand` -> :class:`click.Command`

    .. versionchanged:: 0.8.0
        this class now inherits from :class:`cloup.BaseCommand`.
    """
    pass


class Group(SectionMixin, BaseCommand, click.Group):
    """
    A ``click.Group`` that allows to organize its subcommands in multiple help
    sections and and whose subcommands are, by default, of type
    :class:`cloup.Command`.

    This class is just a :class:`click.Group` mixed with :class:`SectionMixin`
    that overrides the decorators :meth:`command` and :meth:`group` so that
    a ``section`` for the created subcommand can be specified.

    Refer to superclasses for the documentation of all accepted parameters:

    - :class:`SectionMixin`
    - :class:`BaseCommand` -> :class:`click.Command`
    - :class:`click.Group`

    .. versionchanged:: 0.8.0
        this class now inherits from :class:`cloup.BaseCommand`.
    """

    # MyPy complains because "Signature of "group" incompatible with supertype".
    # The supertype signature is (*args, **kwargs) and it is compatible.
    @overload  # type: ignore
    def command(  # Why overloading? Refer to module docstring.
        self, name: Optional[str] = None,
        *,
        cls: None = None,  # Command is cloup.Command
        section: Optional[Section] = None,
        context_settings: Optional[Dict[str, Any]] = None,
        formatter_settings: Optional[Dict[str, Any]] = None,
        help: Optional[str] = None,
        epilog: Optional[str] = None,
        short_help: Optional[str] = None,
        options_metavar: Optional[str] = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        align_option_groups: Optional[bool] = None,
        show_constraints: Optional[bool] = None,
    ) -> Callable[[Callable], Command]:
        ...

    @overload  # type: ignore
    def command(  # Why overloading? Refer to module docstring.
        self, name: Optional[str] = None,
        *,
        cls: Type[ClickCommand],
        section: Optional[Section] = None,
        context_settings: Optional[Dict[str, Any]] = None,
        help: Optional[str] = None,
        epilog: Optional[str] = None,
        short_help: Optional[str] = None,
        options_metavar: Optional[str] = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        **kwargs,
    ) -> Callable[[Callable], ClickCommand]:
        ...

    def command(self, name=None, *, cls=None, section=None, **kwargs):
        """Returns a decorator that creates a new subcommand of this ``Group``
        using the decorated function as callback.

        It takes the same arguments of :func:`command` plus:

        ``section``: ``Optional[Section]``
            if provided, put the subcommand in this section.

        .. versionchanged:: 0.10.0
            all arguments but ``name`` are now keyword-only.
        """

        def decorator(f):
            cmd = command(name=name, cls=cls, **kwargs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator

    # MyPy complains because "Signature of "group" incompatible with supertype".
    # The supertype signature is (*args, **kwargs) and it is compatible.
    @overload  # type: ignore
    def group(  # Why overloading? Refer to module docstring.
        self, name: Optional[str] = None,
        *,
        cls: None = None,  # cls not provided
        section: Optional[Section] = None,
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
    ) -> Callable[[Callable], 'Group']:
        ...

    @overload
    def group(  # Why overloading? Refer to module docstring.
        self, name: Optional[str] = None, *,
        cls: Type[ClickGroup],
        section: Optional[Section] = None,
        invoke_without_command: bool = False,
        no_args_is_help: bool = False,
        context_settings: Optional[Dict[str, Any]] = None,
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
    ) -> Callable[[Callable], ClickGroup]:
        ...

    def group(self, name=None, *, cls=None, section=None, **kwargs):
        """Returns a decorator that creates a new subcommand of this ``Group``
        using the decorated function as callback.

        It takes the same argument of :func:`group` plus:

        ``section``: ``Optional[Section]``
            if provided, put the subcommand in this section.

        .. versionchanged:: 0.10.0
            all arguments but ``name`` are now keyword-only.
        """

        def decorator(f):
            cmd = group(name=name, cls=cls, **kwargs)(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator


@overload  # Why overloading? Refer to module docstring.
def command(
    name: Optional[str] = None,
    *,
    cls: None = None,
    context_settings: Optional[Dict[str, Any]] = None,
    formatter_settings: Optional[Dict[str, Any]] = None,
    help: Optional[str] = None,
    short_help: Optional[str] = None,
    epilog: Optional[str] = None,
    options_metavar: Optional[str] = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    align_option_groups: Optional[bool] = None,
    show_constraints: Optional[bool] = None
) -> Callable[[Callable], Command]:
    ...


@overload
def command(
    name: Optional[str] = None,
    *,
    cls: Type[ClickCommand],
    context_settings: Optional[Dict[str, Any]] = None,
    help: Optional[str] = None,
    short_help: Optional[str] = None,
    epilog: Optional[str] = None,
    options_metavar: Optional[str] = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    **kwargs
) -> Callable[[Callable], ClickCommand]:
    ...


# noinspection PyIncorrectDocstring
def command(name=None, *, cls=None, **kwargs):
    """
    Returns a decorator that creates a new command using the decorated function
    as callback.

    The only differences with respect to ``click.command`` are:

    - the default command class is :class:`cloup.Command`
    - supports constraints, provided that ``cls`` inherits from ``ConstraintMixin``
      like ``cloup.Command`` (the default)
    - this function has detailed type hints and uses generics for the ``cls``
      argument and return type.

    Note that the following arguments are about Cloup-specific features and are
    not supported by all ``click.Command``, so if you provide a custom ``cls``
    make sure you don't ne:

    - ``formatter_settings``
    - ``align_option_groups`` (``cls`` needs to inherit from ``OptionGroupMixin)
    - ``show_constraints`` (``cls`` needs to inherit ``ConstraintMixin).

    .. versionchanged:: 0.10.0
        this function is now generic: the return type depends on what you provide
        as ``cls`` argument.

    .. versionchanged:: 0.9.0
        all arguments but ``name`` are now keyword-only arguments.

    :param name:
        the name of the command to use unless a group overrides it.
    :param cls:
        the command class to instantiate.
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
    :param align_option_groups:
        whether to align the columns of all option groups' help sections.
        This is also available as a context setting having a lower priority
        than this attribute. Given that this setting should be consistent
        across all you commands, you should probably use the context
        setting only.
    :param show_constraints:
        whether to include a "Constraint" section in the command help. This
        is also available as a context setting having a lower priority than
        this attribute.
    :param kwargs:
        any other argument accepted by the instantiated command class (``cls``).
    """

    def decorator(f):
        if hasattr(f, '__constraints'):
            if cls and not issubclass(cls, ConstraintMixin):
                raise TypeError(
                    f"a Command must inherit from cloup.ConstraintMixin to support "
                    f"constraints; {cls} doesn't")
            constraints = tuple(reversed(f.__constraints))
            del f.__constraints
            kwargs['constraints'] = constraints

        cmd_cls = cls if cls is not None else Command
        try:
            return click.command(name, cls=cmd_cls, **kwargs)(f)
        except TypeError as error:
            raise _process_unexpected_kwarg_error(error, _ARGS_INFO, cls)

    return decorator


@overload  # Why overloading? Refer to module docstring.
def group(
    name: Optional[str] = None,
    *,
    cls: None = None,
    sections: Iterable[Section] = (),
    align_sections: Optional[bool] = None,
    invoke_without_command: bool = False,
    no_args_is_help: bool = False,
    context_settings: Optional[Dict[str, Any]] = None,
    formatter_settings: Dict[str, Any] = {},
    help: Optional[str] = None,
    short_help: Optional[str] = None,
    epilog: Optional[str] = None,
    options_metavar: Optional[str] = "[OPTIONS]",
    subcommand_metavar: Optional[str] = None,
    add_help_option: bool = True,
    chain: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
) -> Callable[[Callable], Group]:
    ...


@overload
def group(
    name: Optional[str] = None,
    *,
    cls: Type[ClickGroup],
    invoke_without_command: bool = False,
    no_args_is_help: bool = False,
    context_settings: Optional[Dict[str, Any]] = None,
    help: Optional[str] = None,
    short_help: Optional[str] = None,
    epilog: Optional[str] = None,
    options_metavar: Optional[str] = "[OPTIONS]",
    subcommand_metavar: Optional[str] = None,
    add_help_option: bool = True,
    chain: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
    **kwargs
) -> Callable[[Callable], ClickGroup]:
    ...


def group(name=None, *, cls=None, **kwargs):
    """
    Returns a decorator that instantiates a ``Group`` (or a subclass of it)
    using the decorated function as callback.

    .. versionchanged:: 0.10.0
        the ``cls`` argument can now be any ``click.Group`` (previously had to
        be a ``cloup.Group``) and the type of the instantiated command matches
        it (previously, the type was ``cloup.Group`` even if ``cls`` was a subclass
        of it).

    .. versionchanged:: 0.9.0
        all arguments but ``name`` are now keyword-only arguments.

    :param name:
        the name of the command to use unless a group overrides it.
    :param cls:
        the ``click.Group`` (sub)class to instantiate. This is ``cloup.Group``
        by default. Note that some of the arguments are only supported by
        ``cloup.Group``.
    :param sections:
        a list of Section objects containing the subcommands of this ``Group``.
        This argument is only supported by commands inheriting from
        :class:`cloup.SectionMixin`.
    :param align_sections:
        whether to align the columns of all subcommands' help sections.
        This is also available as a context setting having a lower priority
        than this attribute. Given that this setting should be consistent
        across all you commands, you should probably use the context
        setting only.
    :param context_settings:
        an optional dictionary with defaults that are passed to the context object.
    :param formatter_settings:
        arguments for the formatter; you can use :meth:`HelpFormatter.settings`
        to build this dictionary.
    :param help:
        the help string to use for this command.
    :param short_help:
        the short help to use for this command.  This is shown on the command
        listing of the parent command.
    :param epilog:
        like the help string but it's printed at the end of the help page after
        everything else.
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
    if cls is None:
        cls = Group
    elif not issubclass(cls, click.Group):
        raise TypeError(
            'this decorator requires cls to be a click.Group (or a subclass).')

    return command(name=name, cls=cls, **kwargs)


# Side stuff for better error messages

class _ArgInfo(NamedTuple):
    arg_name: str
    requires: Type
    supported_by: Sequence[str] = []


_ARGS_INFO = {
    info.arg_name: info for info in [
        _ArgInfo('formatter_settings', BaseCommand, ['cloup.Command', 'cloup.Group']),
        _ArgInfo('align_option_groups', OptionGroupMixin, ['cloup.Command']),
        _ArgInfo('show_constraints', ConstraintMixin, ['cloup.Command']),
        _ArgInfo('align_sections', SectionMixin, ['cloup.Group'])
    ]
}


def _process_unexpected_kwarg_error(
    error: TypeError, args_info: Dict[str, _ArgInfo], cls: Type[click.Command]
) -> TypeError:
    """Checks if the developer tried to pass a Cloup-specific argument to a ``cls``
    that doesn't support it and if that's the case, augments the error message
    to provide useful more info about the error."""
    import re

    message = str(error)
    match = re.search('|'.join(arg_name for arg_name in args_info), message)
    if match is None:
        return error
    arg = match.group()
    info = args_info[arg]
    extra_info = reindent(f"""\n
        HINT: you set cls={cls} but this class
        doesn't support the argument "{arg}".
        In Cloup, this argument is handled by {info.requires.__name__} and
        it's supported by {", ".join(info.supported_by)}.
    """, 4)
    new_message = message + '\n' + extra_info
    return TypeError(new_message)
