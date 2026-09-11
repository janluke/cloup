"""
This module contains Cloup command classes and decorators.

Note that Cloup commands *are* Click commands. Apart from supporting more
features, Cloup command decorators have detailed type hints and are generics so
that type checkers can precisely infer the type of the returned command based on
the ``cls`` argument.

Why do the decorators have overloads?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The overloads distinguish the default command class from an explicitly supplied
``cls``, preserving the concrete return type for custom command classes. Click
uses the same pattern. A generic parameter with a concrete default still does
not work in MyPy; see https://github.com/python/mypy/issues/3737.

The explicit keyword parameters provide IDE completion and show defaults.
``TypedDict`` and ``Unpack`` can describe shared keyword arguments, but do not
record their default values. The custom-class overloads also allow arbitrary
extra keywords for subclass constructors.

Like Click, Cloup accepts ``cls`` positionally. That form needs an overload of
its own, and it repeats the keyword arguments of the keyword-``cls`` overload so
that they keep being type-checked in both call styles.

A last overload covers the parenthesis-less form (``@command`` instead of
``@command()``), in which the decorated callback takes the place of ``name``.

"""

import inspect
import sys
from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from typing import (
    Any,
    NamedTuple,
    TypeVar,
    cast,
    overload,
)

import click

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

import cloup

from ._context import Context
from ._option_groups import OptionGroupMixin
from ._sections import Section, SectionMixin
from ._util import first_bool, reindent
from .constraints import ConstraintMixin
from .styling import DEFAULT_THEME
from .typing import AnyCallable

# Generic types of ``cls`` args of ``@command`` and ``@group``
C = TypeVar("C", bound=click.Command)
G = TypeVar("G", bound=click.Group)


class Command(ConstraintMixin, OptionGroupMixin, click.Command):
    """A ``click.Command`` supporting option groups and constraints.

    Refer to superclasses for the documentation of all accepted parameters:

    - :class:`ConstraintMixin`
    - :class:`OptionGroupMixin`
    - :class:`click.Command`

    Besides other things, this class also:

    * adds a ``formatter_settings`` instance attribute.

    Refer to :class:`click.Command` for the documentation of all parameters.

    .. versionadded:: 0.8.0
    """

    # The Cloup command contract requires the Cloup context extensions.
    # pyrefly: ignore[bad-override-mutable-attribute]
    context_class: type[Context] = Context

    def __init__(
        self,
        *args: Any,
        aliases: Iterable[str] | None = None,
        formatter_settings: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        #: HelpFormatter options that are merged with ``Context.formatter_settings``
        #: (eventually overriding some values).
        self.aliases: list[str] = [] if aliases is None else list(aliases)
        self.formatter_settings: dict[str, Any] = (
            {} if formatter_settings is None else formatter_settings
        )

    def get_normalized_epilog(self) -> str:
        if self.epilog:
            return inspect.cleandoc(self.epilog)
        return self.epilog or ""

    # Differently from Click, this doesn't indent the epilog.
    @override
    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        if self.epilog:
            assert isinstance(formatter, cloup.HelpFormatter)
            epilog = self.get_normalized_epilog()
            formatter.write_paragraph()
            formatter.write_epilog(epilog)

    @override
    def format_help_text(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        assert isinstance(formatter, cloup.HelpFormatter)
        formatter.write_command_help_text(self)

    def format_aliases(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        if not self.aliases:
            return
        assert isinstance(formatter, cloup.HelpFormatter)
        formatter.write_aliases(self.aliases)

    @override
    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        self.format_usage(ctx, formatter)
        self.format_aliases(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_params(ctx, formatter)
        if self.must_show_constraints(ctx):
            self.format_constraints(ctx, formatter)  # type: ignore
        if isinstance(self, click.Group):
            self.format_commands(ctx, formatter)
        self.format_epilog(ctx, formatter)


class Group(SectionMixin, Command, click.Group):
    """
    A ``click.Group`` that allows to organize its subcommands in multiple help
    sections and whose subcommands are, by default, of type :class:`cloup.Command`.

    Refer to superclasses for the documentation of all accepted parameters:

    - :class:`SectionMixin`
    - :class:`Command`
    - :class:`click.Group`

    Apart from superclasses arguments, the following is the only additional parameter:

    ``show_subcommand_aliases``: ``Optional[bool] = None``
        whether to show subcommand aliases; aliases are shown by default and
        can be disabled using this argument or the homonym context setting.

    .. versionchanged:: 0.14.0
        this class now supports option groups and constraints.

    .. versionadded:: 0.10.0
        the "command aliases" feature, including the ``show_subcommand_aliases``
        parameter/attribute.

    .. versionchanged:: 0.8.0
        this class now inherits from :class:`cloup.BaseCommand`.
    """

    SHOW_SUBCOMMAND_ALIASES: bool = False

    def __init__(
        self,
        *args: Any,
        show_subcommand_aliases: bool | None = None,
        commands: MutableMapping[str, click.Command]
        | Sequence[click.Command]
        | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.show_subcommand_aliases = show_subcommand_aliases
        """Whether to show subcommand aliases."""

        self.alias2name: dict[str, str] = {}
        """Dictionary mapping each alias to a command name."""

        if commands:
            self.add_multiple_commands(commands)

    def add_multiple_commands(
        self, commands: Mapping[str, click.Command] | Sequence[click.Command]
    ) -> None:
        if isinstance(commands, Mapping):
            for name, cmd in commands.items():
                self.add_command(cmd, name=name)
        else:
            for cmd in commands:
                self.add_command(cmd)

    @override
    def add_command(
        self,
        cmd: click.Command,
        name: str | None = None,
        section: Section | None = None,
        fallback_to_default_section: bool = True,
    ) -> None:
        super().add_command(cmd, name, section, fallback_to_default_section)
        name = cast(str, cmd.name) if name is None else name
        aliases = getattr(cmd, "aliases", [])
        for alias in aliases:
            self.alias2name[alias] = name

    def resolve_command_name(self, ctx: click.Context, name: str) -> str | None:
        """Map a string supposed to be a command name or an alias to a normalized
        command name. If no match is found, it returns ``None``."""
        if ctx.token_normalize_func:
            name = ctx.token_normalize_func(name)
        if name in self.commands:
            return name
        return self.alias2name.get(name)

    @override
    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        normalized_name = self.resolve_command_name(ctx, args[0])
        if normalized_name:
            # Replacing this string ensures that super().resolve_command() returns a
            # normalized command name rather than an alias. The technique described in
            # Click's docs doesn't work if the subcommand is added using Group.group
            # passing the "name" argument.
            args[0] = normalized_name
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError as error:
            new_error = self.handle_bad_command_name(
                bad_name=args[0],
                valid_names=[*self.commands, *self.alias2name],
                error=error,
            )
            raise new_error

    def handle_bad_command_name(
        self, bad_name: str, valid_names: list[str], error: click.UsageError
    ) -> click.UsageError:
        """This method is called when a command name cannot be resolved.
        Useful to implement the "Did you mean <x>?" feature.

        :param bad_name: the command name that could not be resolved.
        :param valid_names: the list of valid command names, including aliases.
        :param error: the original error coming from Click.
        :return: the original error or a new one.
        """
        suggestion_error = click.NoSuchCommand(
            bad_name,
            message=str(error),
            possibilities=valid_names,
            ctx=error.ctx,
        )
        return suggestion_error if suggestion_error.possibilities else error

    def must_show_subcommand_aliases(self, ctx: click.Context) -> bool:
        return first_bool(
            self.show_subcommand_aliases,
            getattr(ctx, "show_subcommand_aliases", None),
            Group.SHOW_SUBCOMMAND_ALIASES,
        )

    @override
    def format_subcommand_name(
        self, ctx: click.Context, name: str, cmd: click.Command
    ) -> str:
        aliases = getattr(cmd, "aliases", None)
        if aliases and self.must_show_subcommand_aliases(ctx):
            assert isinstance(ctx, cloup.Context)
            theme = cast(
                cloup.HelpTheme, ctx.formatter_settings.get("theme", DEFAULT_THEME)
            )
            alias_list = self.format_subcommand_aliases(aliases, theme)
            return f"{name} {alias_list}"
        return name

    @staticmethod
    def format_subcommand_aliases(aliases: Sequence[str], theme: cloup.HelpTheme) -> str:
        secondary_style = theme.alias_secondary
        if secondary_style is None or secondary_style == theme.alias:
            return theme.alias(f"({', '.join(aliases)})")
        else:
            return (
                secondary_style("(")
                + secondary_style(", ").join(theme.alias(alias) for alias in aliases)
                + secondary_style(")")
            )

    # Click types these methods as ``(*args: Any, **kwargs: Any)``, i.e. as an
    # unspecified signature, so any signature naming its arguments is formally
    # narrower. MyPy reads an unspecified supertype signature as "anything goes"
    # and accepts it; Pyrefly has no such rule, hence the suppression. Satisfying
    # Pyrefly would require a trailing ``(*args: Any, **kwargs: Any)`` overload,
    # which would swallow every keyword argument error these overloads exist to
    # catch.
    @overload
    # pyrefly: ignore[bad-override]
    def command(self, name: AnyCallable, /) -> click.Command: ...

    @overload
    def command(  # Why overloading? Refer to module docstring.
        self,
        name: str | None = None,
        cls: None = None,  # default to Group.command_class or cloup.Command
        *,
        aliases: Iterable[str] | None = None,
        section: Section | None = None,
        context_settings: dict[str, Any] | None = None,
        formatter_settings: dict[str, Any] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
        align_option_groups: bool | None = None,
        show_constraints: bool | None = None,
        params: list[click.Parameter] | None = None,
    ) -> Callable[[AnyCallable], click.Command]: ...

    @overload
    def command(  # Why overloading? Refer to module docstring.
        self,
        name: str | None = None,
        *,
        aliases: Iterable[str] | None = None,
        cls: type[C],
        section: Section | None = None,
        context_settings: dict[str, Any] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
        params: list[click.Parameter] | None = None,
        **kwargs: Any,
    ) -> Callable[[AnyCallable], C]: ...

    @overload
    def command(  # In this overload: "cls" passed positionally, as Click allows
        self,
        name: str | None,
        cls: type[C],
        *,
        aliases: Iterable[str] | None = None,
        section: Section | None = None,
        context_settings: dict[str, Any] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
        params: list[click.Parameter] | None = None,
        **kwargs: Any,
    ) -> Callable[[AnyCallable], C]: ...

    @override
    def command(
        self,
        name: str | AnyCallable | None = None,
        cls: type[C] | None = None,
        *,
        aliases: Iterable[str] | None = None,
        section: Section | None = None,
        **kwargs: Any,
    ) -> click.Command | Callable[[AnyCallable], click.Command | C]:
        """Return a decorator that creates a new subcommand of this ``Group``
        using the decorated function as callback.

        It takes the same arguments of :func:`command` plus:

        ``section``: ``Optional[Section]``
            if provided, put the subcommand in this section.

        .. versionchanged:: 4.0.0
            the decorator can be applied without parentheses and ``cls`` can be
            passed positionally, like in Click.

        .. versionchanged:: 0.10.0
            all arguments but ``name`` are now keyword-only.
        """
        func, name = _resolve_decorator_first_arg(name)
        make_command = command(
            name=name,
            cls=(self.command_class if cls is None else cls),
            aliases=aliases,
            **kwargs,
        )

        def decorator(f: AnyCallable) -> click.Command:
            cmd = make_command(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator(func) if func is not None else decorator

    # Narrower than Click's for the same reason as command(); see the note there.
    @overload
    # pyrefly: ignore[bad-override]
    def group(self, name: AnyCallable, /) -> click.Group: ...

    @overload
    def group(  # Why overloading? Refer to module docstring.
        self,
        name: str | None = None,
        cls: None = None,  # cls not provided
        *,
        aliases: Iterable[str] | None = None,
        section: Section | None = None,
        sections: Iterable[Section] = (),
        align_sections: bool | None = None,
        invoke_without_command: bool = False,
        no_args_is_help: bool = False,
        context_settings: dict[str, Any] | None = None,
        formatter_settings: dict[str, Any] | None = None,
        align_option_groups: bool | None = None,
        show_constraints: bool | None = None,
        params: list[click.Parameter] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        subcommand_metavar: str | None = None,
        add_help_option: bool = True,
        chain: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
        show_subcommand_aliases: bool = False,
    ) -> Callable[[AnyCallable], click.Group]: ...

    @overload
    def group(  # Why overloading? Refer to module docstring.
        self,
        name: str | None = None,
        *,
        aliases: Iterable[str] | None = None,
        cls: type[G],
        section: Section | None = None,
        invoke_without_command: bool = False,
        no_args_is_help: bool = False,
        context_settings: dict[str, Any] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        subcommand_metavar: str | None = None,
        add_help_option: bool = True,
        chain: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
        params: list[click.Parameter] | None = None,
        **kwargs: Any,
    ) -> Callable[[AnyCallable], G]: ...

    @overload
    def group(  # In this overload: "cls" passed positionally, as Click allows
        self,
        name: str | None,
        cls: type[G],
        *,
        aliases: Iterable[str] | None = None,
        section: Section | None = None,
        invoke_without_command: bool = False,
        no_args_is_help: bool = False,
        context_settings: dict[str, Any] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        subcommand_metavar: str | None = None,
        add_help_option: bool = True,
        chain: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
        params: list[click.Parameter] | None = None,
        **kwargs: Any,
    ) -> Callable[[AnyCallable], G]: ...

    @override
    def group(
        self,
        name: str | AnyCallable | None = None,
        cls: type[G] | None = None,
        *,
        aliases: Iterable[str] | None = None,
        section: Section | None = None,
        **kwargs: Any,
    ) -> click.Group | Callable[[AnyCallable], click.Group | G]:
        """Return a decorator that creates a new subcommand of this ``Group``
        using the decorated function as callback.

        It takes the same argument of :func:`group` plus:

        ``section``: ``Optional[Section]``
            if provided, put the subcommand in this section.

        .. versionchanged:: 4.0.0
            the decorator can be applied without parentheses and ``cls`` can be
            passed positionally, like in Click.

        .. versionchanged:: 0.10.0
            all arguments but ``name`` are now keyword-only.
        """
        func, name = _resolve_decorator_first_arg(name)
        make_group = group(
            name=name, cls=cls or self._default_group_class(), aliases=aliases, **kwargs
        )

        def decorator(f: AnyCallable) -> click.Group | G:
            cmd = make_group(f)
            self.add_command(cmd, section=section)
            return cmd

        return decorator(func) if func is not None else decorator

    @classmethod
    def _default_group_class(cls) -> type[click.Group] | None:
        if cls.group_class is None:
            return None
        if cls.group_class is type:
            return cls
        else:
            return cast(type[click.Group], cls.group_class)


# Why overloading? Refer to module docstring.
@overload  # In this overload: bare decorator, i.e. "@command" without parentheses
def command(name: AnyCallable, /) -> Command: ...


@overload  # In this overload: "cls: None = None"
def command(
    name: str | None = None,
    cls: None = None,
    *,
    aliases: Iterable[str] | None = None,
    context_settings: dict[str, Any] | None = None,
    formatter_settings: dict[str, Any] | None = None,
    help: str | None = None,
    short_help: str | None = None,
    epilog: str | None = None,
    options_metavar: str | None = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool | str = False,
    align_option_groups: bool | None = None,
    show_constraints: bool | None = None,
    params: list[click.Parameter] | None = None,
) -> Callable[[AnyCallable], Command]: ...


@overload
def command(  # In this overload: "cls: ClickCommand"
    name: str | None = None,
    *,
    aliases: Iterable[str] | None = None,
    cls: type[C],
    context_settings: dict[str, Any] | None = None,
    help: str | None = None,
    short_help: str | None = None,
    epilog: str | None = None,
    options_metavar: str | None = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool | str = False,
    params: list[click.Parameter] | None = None,
    **kwargs: Any,
) -> Callable[[AnyCallable], C]: ...


@overload
def command(  # In this overload: "cls" passed positionally, as Click allows
    name: str | None,
    cls: type[C],
    *,
    aliases: Iterable[str] | None = None,
    context_settings: dict[str, Any] | None = None,
    help: str | None = None,
    short_help: str | None = None,
    epilog: str | None = None,
    options_metavar: str | None = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool | str = False,
    params: list[click.Parameter] | None = None,
    **kwargs: Any,
) -> Callable[[AnyCallable], C]: ...


# noinspection PyIncorrectDocstring
def command(
    name: str | AnyCallable | None = None,
    cls: type[C] | None = None,
    *,
    aliases: Iterable[str] | None = None,
    **kwargs: Any,
) -> Command | Callable[[AnyCallable], Command | C]:
    """
    Return a decorator that creates a new command using the decorated function
    as callback.

    The only differences with respect to ``click.command`` are:

    - the default command class is :class:`cloup.Command`
    - supports constraints, provided that ``cls`` inherits from ``ConstraintMixin``
      like ``cloup.Command`` (the default)
    - this function has detailed type hints and uses generics for the ``cls``
      argument and return type.

    Like in Click, the decorator can be applied with or without parentheses and
    ``cls`` can be passed positionally.

    Note that the following arguments are about Cloup-specific features and are
    not supported by all ``click.Command``, so if you provide a custom ``cls``
    make sure you don't set these:

    - ``formatter_settings``
    - ``align_option_groups`` (``cls`` needs to inherit from ``OptionGroupMixin``)
    - ``show_constraints`` (``cls`` needs to inherit ``ConstraintMixin``).

    .. versionchanged:: 4.0.0
        the decorator can be applied without parentheses and ``cls`` can be passed
        positionally, like in Click.

    .. versionchanged:: 0.10.0
        this function is now generic: the return type depends on what you provide
        as ``cls`` argument.

    .. versionchanged:: 0.9.0
        all arguments but ``name`` are now keyword-only arguments.

    :param name:
        the name of the command to use unless a group overrides it.
    :param aliases:
        alternative names for this command. If ``cls`` is not a Cloup command class,
        aliases will be stored in the instantiated command by monkey-patching
        and aliases won't be documented in the help page of the command.
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
        issues a message indicating that the command is deprecated. A string
        provides a custom deprecation message.
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
    :param params:
        **(click >= 8.1.0)** a list of parameters (:class:`Argument` and
        :class:`Option` instances). Params added with ``@option`` and ``@argument``
        are appended to the end of the list if given.
    :param kwargs:
        any other argument accepted by the instantiated command class (``cls``).
    """
    func, name = _resolve_decorator_first_arg(name)

    def decorator(f: AnyCallable) -> Command | C:
        if hasattr(f, "__cloup_constraints__"):
            if cls and not issubclass(cls, ConstraintMixin):
                raise TypeError(
                    f"a `Command` must inherit from `cloup.ConstraintMixin` to support "
                    f"constraints; `{cls}` doesn't"
                )
            constraints = tuple(reversed(getattr(f, "__cloup_constraints__")))
            delattr(f, "__cloup_constraints__")
            kwargs["constraints"] = constraints

        cmd_cls: type[Command | C] = cls if cls is not None else Command
        try:
            cmd = click.command(name, cls=cmd_cls, **kwargs)(f)
            if aliases:
                cmd.aliases = list(aliases)  # type: ignore
            return cmd
        except TypeError as error:
            raise _process_unexpected_kwarg_error(error, _ARGS_INFO, cmd_cls)

    return decorator(func) if func is not None else decorator


# Why overloading? Refer to module docstring.
@overload  # In this overload: bare decorator, i.e. "@group" without parentheses
def group(name: AnyCallable, /) -> Group: ...


@overload
def group(
    name: str | None = None,
    cls: None = None,
    *,
    aliases: Iterable[str] | None = None,
    sections: Iterable[Section] = (),
    align_sections: bool | None = None,
    invoke_without_command: bool = False,
    no_args_is_help: bool = False,
    context_settings: dict[str, Any] | None = None,
    formatter_settings: dict[str, Any] | None = None,
    align_option_groups: bool | None = None,
    show_constraints: bool | None = None,
    help: str | None = None,
    short_help: str | None = None,
    epilog: str | None = None,
    options_metavar: str | None = "[OPTIONS]",
    subcommand_metavar: str | None = None,
    add_help_option: bool = True,
    chain: bool = False,
    hidden: bool = False,
    deprecated: bool | str = False,
    params: list[click.Parameter] | None = None,
    show_subcommand_aliases: bool = False,
) -> Callable[[AnyCallable], Group]: ...


@overload
def group(
    name: str | None = None,
    *,
    cls: type[G],
    aliases: Iterable[str] | None = None,
    invoke_without_command: bool = False,
    no_args_is_help: bool = False,
    context_settings: dict[str, Any] | None = None,
    help: str | None = None,
    short_help: str | None = None,
    epilog: str | None = None,
    options_metavar: str | None = "[OPTIONS]",
    subcommand_metavar: str | None = None,
    add_help_option: bool = True,
    chain: bool = False,
    hidden: bool = False,
    deprecated: bool | str = False,
    params: list[click.Parameter] | None = None,
    **kwargs: Any,
) -> Callable[[AnyCallable], G]: ...


@overload
def group(  # In this overload: "cls" passed positionally, as Click allows
    name: str | None,
    cls: type[G],
    *,
    aliases: Iterable[str] | None = None,
    invoke_without_command: bool = False,
    no_args_is_help: bool = False,
    context_settings: dict[str, Any] | None = None,
    help: str | None = None,
    short_help: str | None = None,
    epilog: str | None = None,
    options_metavar: str | None = "[OPTIONS]",
    subcommand_metavar: str | None = None,
    add_help_option: bool = True,
    chain: bool = False,
    hidden: bool = False,
    deprecated: bool | str = False,
    params: list[click.Parameter] | None = None,
    **kwargs: Any,
) -> Callable[[AnyCallable], G]: ...


def group(
    name: str | AnyCallable | None = None, cls: type[G] | None = None, **kwargs: Any
) -> click.Group | Callable[[AnyCallable], click.Group]:
    """
    Return a decorator that instantiates a ``Group`` (or a subclass of it)
    using the decorated function as callback.

    As with :func:`command`, the decorator can be applied with or without
    parentheses and ``cls`` can be passed positionally.

    .. versionchanged:: 4.0.0
        the decorator can be applied without parentheses and ``cls`` can be passed
        positionally, like in Click.

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
    :param hidden:
        hide this command from help outputs.
    :param deprecated:
        issues a message indicating that the command is deprecated. A string
        provides a custom deprecation message.
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
        if this is set to `True`, chaining of multiple subcommands is enabled.
        This restricts the form of commands in that they cannot have optional
        arguments but it allows multiple commands to be chained together.
    :param params:
        **(click >= 8.1.0)** a list of parameters (:class:`Argument` and
        :class:`Option` instances). Params added with ``@option`` and ``@argument``
        are appended to the end of the list if given.
    :param kwargs:
        any other argument accepted by the instantiated command class.
    """
    if cls is not None and not issubclass(cls, click.Group):
        raise TypeError(
            "this decorator requires `cls` to be a `click.Group` (or a subclass)"
        )
    func, name = _resolve_decorator_first_arg(name)
    group_cls: type[click.Group] = Group if cls is None else cls
    make_group = command(name=name, cls=group_cls, **kwargs)
    return make_group(func) if func is not None else make_group


def _resolve_decorator_first_arg(
    name: str | AnyCallable | None,
) -> tuple[AnyCallable | None, str | None]:
    """Resolve the first argument of a command decorator into ``(func, name)``.

    Click's decorators can be applied without parentheses, in which case the
    decorated callback takes the place of ``name``. Cloup mirrors that.
    """
    if callable(name):
        return name, None
    return None, name


# Side stuff for better error messages


class _ArgInfo(NamedTuple):
    arg_name: str
    requires: type[Any]
    supported_by: str = ""


_ARGS_INFO = {
    info.arg_name: info
    for info in [
        _ArgInfo("formatter_settings", Command, "both `Command` and `Group`"),
        _ArgInfo("align_option_groups", OptionGroupMixin, "both `Command` and `Group`"),
        _ArgInfo("show_constraints", ConstraintMixin, "both `Command` and `Group`"),
        _ArgInfo("align_sections", SectionMixin, "`Group`"),
    ]
}


def _process_unexpected_kwarg_error(
    error: TypeError, args_info: dict[str, _ArgInfo], cls: type[click.Command]
) -> TypeError:
    """Check if the developer tried to pass a Cloup-specific argument to a ``cls``
    that doesn't support it and if that's the case, augments the error message
    to provide useful more info about the error."""
    import re

    message = str(error)
    match = re.search("|".join(arg_name for arg_name in args_info), message)
    if match is None:
        return error
    arg = match.group()
    info = args_info[arg]
    extra_info = reindent(
        f"""\n
        Hint: you set `cls={cls}` but this class doesn't support the argument `{arg}`.
        In Cloup, this argument is supported by `{info.supported_by}`
        via `{info.requires.__name__}`.
    """,
        4,
    )
    new_message = message + "\n" + extra_info
    return TypeError(new_message)
