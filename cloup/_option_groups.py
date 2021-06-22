"""
Implements support to option group.
"""
from collections import defaultdict
from typing import (
    Callable, Iterable, List, Optional, Sequence, TYPE_CHECKING, Tuple, cast, overload,
)

import click
from click import Option, Parameter

from cloup._params import option
from cloup._util import C, coalesce, make_repr
from cloup.constraints import Constraint
from cloup.formatting import HelpSection, ensure_is_cloup_formatter

if TYPE_CHECKING:
    from cloup._params import OptionAdder

OptionGroupAdder = Callable[[C], C]
"""A decorator that registers an option group to the wrapped function."""


class OptionGroup:
    def __init__(self, name: str,
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
        if not name:
            raise ValueError('name is a mandatory argument')   # pragma: no cover
        self.name = name
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
        return [opt.get_help_record(ctx) for opt in self if not opt.hidden]

    def option(self, *param_decls, **attrs):
        return option(*param_decls, group=self, **attrs)

    def __iter__(self):
        return iter(self.options)

    def __getitem__(self, i: int) -> click.Option:
        return self.options[i]

    def __len__(self) -> int:
        return len(self.options)

    def __repr__(self) -> str:
        return make_repr(self, self.name, help=self.help, options=self.options)

    def __str__(self) -> str:
        return make_repr(
            self, self.name, options=[opt.name for opt in self.options])


def has_option_group(param) -> bool:
    return hasattr(param, 'group') and param.group is not None


def get_option_group_of(param, default=None):
    return param.group if has_option_group(param) else default


# noinspection PyMethodMayBeStatic
class OptionGroupMixin:
    """Implements support to option groups.

    .. versionchanged:: 0.8.0
        This mixin now relies on ``cloup.HelpFormatter`` to align help sections.
        If a ``click.HelpFormatter`` is used with a ``TypeError`` is raised.

    .. versionchanged:: 0.8.0
        Removed ``format_option_group``. Added ``get_default_option_group`` and
        ``make_option_group_help_section``.

    .. versionadded:: 0.5.0

    .. important::
        In order to check the constraints defined on the option groups,
        a command must inherits from :class:`cloup.ConstraintMixin` too!
    """

    def __init__(
        self, *args, align_option_groups: Optional[bool] = None, **kwargs
    ):
        self.align_option_groups = align_option_groups
        self.option_groups, self.ungrouped_options = \
            self._option_groups_from_params(kwargs['params'])
        super().__init__(*args, **kwargs)  # type: ignore

    @staticmethod
    def _option_groups_from_params(
        params: List[Parameter]
    ) -> Tuple[List[OptionGroup], List[Option]]:

        options_by_group = defaultdict(list)
        for param in params:
            if isinstance(param, click.Option):
                grp = get_option_group_of(param)
                options_by_group[grp].append(param)

        ungrouped_options = options_by_group.pop(None, [])
        option_groups = list(options_by_group.keys())
        for group, options in options_by_group.items():
            group.options = options

        return option_groups, ungrouped_options

    def get_ungrouped_options(self, ctx: click.Context) -> Sequence[click.Option]:
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
            heading=group.name,
            definitions=group.get_help_records(ctx),
            help=group.help,
            constraint=group.constraint.help(ctx) if group.constraint else None
        )

    def must_align_option_groups(
        self, ctx: Optional[click.Context], default=True
    ) -> bool:
        """
        .. versionadded:: 0.8.0
        """
        align = coalesce(
            self.align_option_groups,
            getattr(ctx, 'align_option_groups', None),
            default,
        )
        return cast(bool, align)

    def get_default_option_group(self, ctx: click.Context) -> OptionGroup:
        """
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


@overload
def option_group(
    name: str,
    help: str,
    *options: 'OptionAdder',
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> OptionGroupAdder:
    ...


@overload
def option_group(
    name: str,
    *options: 'OptionAdder',
    help: Optional[str] = None,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> OptionGroupAdder:
    ...


# noinspection PyIncorrectDocstring
def option_group(name, *args, **kwargs):
    """
    Returns a decorator that annotates a function with an option group.

    The ``help`` is an optional description and can be provided either as keyword
    argument or as 2nd positional argument after the ``name`` of the group::

        # help as keyword argument
        @option_group(name, *options, help=None, ...)

        # help as 2nd positional argument
        @option_group(name, help, *options, ...)

    .. versionchanged:: 0.9.0
        In order to support the decorator :func:`cloup.constrained_params`,
        ``@option_group`` now allows each input decorators to add multiple
        options.

    :param name:
        this is shown as heading of the help section describing the option group.
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
        return _option_group(name, options=args[1:], help=args[0], **kwargs)
    else:
        return _option_group(name, options=args, **kwargs)


def _option_group(
    name: str,
    options: Sequence['OptionAdder'],
    help: Optional[str] = None,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> OptionGroupAdder:
    if not options:
        raise ValueError('you must provide at least one option')

    def decorator(f):
        opt_group = OptionGroup(name, help=help, constraint=constraint, hidden=hidden)
        if not hasattr(f, '__click_params__'):
            f.__click_params__ = []
        for add_option in reversed(options):
            prev_len = len(f.__click_params__)
            add_option(f)
            added_options = f.__click_params__[prev_len:]
            for new_option in added_options:
                if not isinstance(new_option, Option):
                    raise TypeError("only `Option`'s are allowed in option groups")
                if has_option_group(new_option):
                    raise ValueError(
                        f'{new_option} was first assigned to {new_option.group} and then '
                        f'passed as argument to @option_group({name!r}, ...)'
                    )
                new_option.group = opt_group
                if hidden:
                    new_option.hidden = True
        return f

    return decorator
