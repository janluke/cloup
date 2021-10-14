"""
Implements the "option groups" feature.
"""
from collections import defaultdict
from typing import (
    Callable, Iterable, Iterator, List, Optional, Sequence, Tuple, overload,
)

import click
from click import Option, Parameter

from cloup._params import option
from cloup._util import first_bool, make_repr
from cloup.constraints import Constraint
from cloup.formatting import HelpSection, ensure_is_cloup_formatter
from cloup.typing import Decorator, F


class OptionGroup:
    def __init__(self, title: str,
                 help: Optional[str] = None,
                 constraint: Optional[Constraint] = None,
                 hidden: bool = False):
        """Contains the information of an option group and identifies it.
        Note that, as far as the clients of this library are concerned, an
        ``OptionGroups`` acts as a "marker" for options, not as a container for
        related options. When you call ``@optgroup.option(...)`` you are not
        adding an option to a container, you are just adding an option marked
        with this option group.

        .. versionadded:: 0.8.0
            The ``hidden`` parameter.
        """
        if not title:
            raise ValueError('name is a mandatory argument')  # pragma: no cover
        self.title = title
        self.help = help
        self._options: Sequence[click.Option] = []
        self.constraint = constraint
        self.hidden = hidden

    @property
    def options(self) -> Sequence[click.Option]:
        return self._options

    @options.setter
    def options(self, options: Iterable[click.Option]) -> None:
        self._options = opts = tuple(options)
        if self.hidden:
            for opt in opts:
                opt.hidden = True
        elif all(opt.hidden for opt in opts):
            self.hidden = True

    def get_help_records(self, ctx: click.Context) -> List[Tuple[str, str]]:
        if self.hidden:
            return []
        return [
            opt.get_help_record(ctx) for opt in self if not opt.hidden  # type: ignore
        ]  # get_help_record() should return None only if opt.hidden

    def option(self, *param_decls, **attrs) -> Callable[[F], F]:
        """Refer to :func:`cloup.option`."""
        return option(*param_decls, group=self, **attrs)

    def __iter__(self) -> Iterator[click.Option]:
        return iter(self.options)

    def __getitem__(self, i: int) -> click.Option:
        return self.options[i]

    def __len__(self) -> int:
        return len(self.options)

    def __repr__(self) -> str:
        return make_repr(self, self.title, help=self.help, options=self.options)

    def __str__(self) -> str:
        return make_repr(
            self, self.title, options=[opt.name for opt in self.options])


def has_option_group(param) -> bool:
    return getattr(param, 'group', None) is not None


def get_option_group_of(param) -> Optional[OptionGroup]:
    return getattr(param, 'group', None)


# noinspection PyMethodMayBeStatic
class OptionGroupMixin:
    """Implements support to option groups.

    .. versionchanged:: 0.8.0
        this mixin now relies on ``cloup.HelpFormatter`` to align help sections.
        If a ``click.HelpFormatter`` is used with a ``TypeError`` is raised.

    .. versionchanged:: 0.8.0
        removed ``format_option_group``. Added ``get_default_option_group`` and
        ``make_option_group_help_section``.

    .. versionadded:: 0.5.0

    .. important::
        In order to check the constraints defined on the option groups,
        a command must inherits from :class:`cloup.ConstraintMixin` too!
    """

    def __init__(
        self, *args, align_option_groups: Optional[bool] = None, **kwargs
    ):
        """
        :param align_option_groups:
            whether to align the columns of all option groups' help sections.
            This is also available as a context setting having a lower priority
            than this attribute. Given that this setting should be consistent
            across all you commands, you should probably use the context
            setting only.
        :param args:
            positional arguments forwarded to the next class in the MRO
        :param kwargs:
            keyword arguments forwarded to the next class in the MRO
        """
        self.align_option_groups = align_option_groups
        params = kwargs.get('params') or []
        option_groups, ungrouped_options = self._option_groups_from_params(params)

        self.option_groups = option_groups
        """List of all option groups, except the "default option group"."""

        self.ungrouped_options = ungrouped_options
        """List of options not explicitly assigned to an user-defined option group.
        These options will be included in the "default option group".
        **Note:** this list does not include options added automatically by Click
        based on context settings, like the ``--help`` option; use the
        :meth:`get_ungrouped_options` method if you need the real full list
        (which needs a ``Context`` object)."""

        super().__init__(*args, **kwargs)  # type: ignore

    @staticmethod
    def _option_groups_from_params(
        params: List[Parameter]
    ) -> Tuple[List[OptionGroup], List[Option]]:

        options_by_group = defaultdict(list)
        ungrouped_options = []
        for param in params:
            if not isinstance(param, click.Option):
                continue
            grp = get_option_group_of(param)
            if grp is None:
                ungrouped_options.append(param)
            else:
                options_by_group[grp].append(param)

        option_groups = list(options_by_group.keys())
        for group, options in options_by_group.items():
            group.options = options

        return option_groups, ungrouped_options

    def get_ungrouped_options(self, ctx: click.Context) -> Sequence[click.Option]:
        """Returns options not explicitly assigned to an option group
        (eventually including the ``--help`` option), i.e. options that will be
        part of the "default option group"."""
        help_option = ctx.command.get_help_option(ctx)
        if help_option is not None:
            return self.ungrouped_options + [help_option]
        else:
            return self.ungrouped_options

    def make_option_group_help_section(
        self, group: OptionGroup, ctx: click.Context
    ) -> HelpSection:
        """Returns a HelpSection for an OptionGroup, i.e. an object containing
        the title, the optional description and the options' definitions for
        this option group.

        .. versionadded:: 0.8.0
        """
        return HelpSection(
            heading=group.title,
            definitions=group.get_help_records(ctx),
            help=group.help,
            constraint=group.constraint.help(ctx) if group.constraint else None
        )

    def must_align_option_groups(
        self, ctx: Optional[click.Context], default: bool = True
    ) -> bool:
        """
        Returns ``True`` if the help sections of all options groups should have
        their columns aligned.

        .. versionadded:: 0.8.0
        """
        return first_bool(
            self.align_option_groups,
            getattr(ctx, 'align_option_groups', None),
            default,
        )

    def get_default_option_group(self, ctx: click.Context) -> OptionGroup:
        """
        Returns an ``OptionGroup`` instance for the options not explicitly
        assigned to an option group, eventually including the ``--help`` option.

        .. versionadded:: 0.8.0
        """
        default_group = OptionGroup('Other options')
        default_group.options = self.get_ungrouped_options(ctx)
        return default_group

    def format_options(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        formatter = ensure_is_cloup_formatter(formatter)
        visible_sections = [
            self.make_option_group_help_section(group, ctx)
            for group in self.option_groups
            if not group.hidden
        ]
        if not visible_sections:  # No visible option groups. No custom formatting needed.
            return super().format_options(ctx, formatter)  # type: ignore

        default_group = self.get_default_option_group(ctx)
        if not default_group.hidden:
            visible_sections.append(
                self.make_option_group_help_section(default_group, ctx))

        formatter.write_many_sections(
            visible_sections,
            aligned=self.must_align_option_groups(ctx),
        )
        if isinstance(self, click.MultiCommand):
            self.format_commands(ctx, formatter)


@overload
def option_group(
    title: str,
    help: str,
    *options: Decorator,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> Callable[[F], F]:
    ...


@overload
def option_group(
    title: str,
    *options: Decorator,
    help: Optional[str] = None,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> Callable[[F], F]:
    ...


# noinspection PyIncorrectDocstring
def option_group(title, *args, **kwargs):
    """
    Returns a decorator that annotates a function with an option group.

    The ``help`` argument is an optional description and can be provided either
    as keyword argument or as 2nd positional argument after the ``name`` of
    the group::

        # help as keyword argument
        @option_group(name, *options, help=None, ...)

        # help as 2nd positional argument
        @option_group(name, help, *options, ...)

    .. versionchanged:: 0.9.0
        in order to support the decorator :func:`cloup.constrained_params`,
        ``@option_group`` now allows each input decorators to add multiple
        options.

    :param title:
        title of the help section describing the option group.
    :param help:
        an optional description shown below the name; can be provided as keyword
        argument or 2nd positional argument.
    :param options:
        an arbitrary number of decorators like ``click.option``, which attach
        one or multiple options to the decorated command function.
    :param constraint:
        an optional instance of :class:`~cloup.constraints.Constraint`
        (see :doc:`Constraints </pages/constraints>` for more info);
        a description of the constraint will be shown between squared brackets
        aside the option group title (or below it if too long).
    :param hidden:
        if ``True``, the option group and all its options are hidden from the help page
        (all contained options will have their ``hidden`` attribute set to ``True``).
    """
    if args and isinstance(args[0], str):
        return _option_group(title, options=args[1:], help=args[0], **kwargs)
    else:
        return _option_group(title, options=args, **kwargs)


def _option_group(
    title: str,
    options: Callable[[F], F],
    help: Optional[str] = None,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> Callable[[F], F]:
    if not isinstance(title, str):
        raise TypeError(
            'the first argument of @option_group must be its title, a string. '
            'You probably forgot it!'
        )

    if not options:
        raise ValueError('you must provide at least one option')

    def decorator(f):
        opt_group = OptionGroup(title, help=help, constraint=constraint, hidden=hidden)
        if not hasattr(f, '__click_params__'):
            f.__click_params__ = []
        for add_option in reversed(options):
            prev_len = len(f.__click_params__)
            add_option(f)
            added_options = f.__click_params__[prev_len:]
            for new_option in added_options:
                if not isinstance(new_option, Option):
                    raise TypeError(
                        "only parameter of type `Option` can be added to option groups")
                if has_option_group(new_option):
                    raise ValueError(
                        f'{new_option} was first assigned to {new_option.group} and then '
                        f'passed as argument to @option_group({title!r}, ...)'
                    )
                new_option.group = opt_group
                if hidden:
                    new_option.hidden = True
        return f

    return decorator
