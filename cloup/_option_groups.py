"""
Implements support to option group.
"""
from collections import defaultdict
from typing import (
    Callable, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, cast, overload,
)

import click
from click import Option, Parameter

from cloup._util import coalesce, make_repr
from cloup.constraints import Constraint
from cloup.formatting import HelpSection, ensure_is_cloup_formatter

C = TypeVar('C', bound=Callable)

#: A decorator that registers an option to the wrapped function
OptionDecorator = Callable[[C], C]

#: A decorator that registers an option group to the wrapped function
OptionGroupDecorator = Callable[[C], C]


class OptionGroup:
    def __init__(self, name: str,
                 help: Optional[str] = None,
                 constraint: Optional[Constraint] = None,
                 hidden: bool = False):
        """
        .. versionadded: 0.8.0
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


class GroupedOption(click.Option):
    """ A click.Option with an extra field ``group`` of type OptionGroup """

    def __init__(self, *args, group: Optional[OptionGroup] = None, **attrs):
        super().__init__(*args, **attrs)
        self.group = group


def has_option_group(param) -> bool:
    return hasattr(param, 'group') and param.group is not None


def get_option_group_of(param, default=None):
    return param.group if has_option_group(param) else default


# noinspection PyMethodMayBeStatic
class OptionGroupMixin:
    """Implements support to option groups.

    .. versionchanged:: 0.8.0
        * This mixin now relies on ``cloup.HelpFormatter`` to align help sections.
          If a ``click.HelpFormatter`` is used with a ``TypeError`` is raised.
        * Removed ``format_option_group``
        * Added ``get_default_option_group``.
        * Added ``make_option_group_help_section``.

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
            description=group.help,
            constraint=group.constraint.help(ctx) if group.constraint else None
        )

    def must_align_option_groups(
        self, ctx: Optional[click.Context], default=True
    ) -> bool:
        """
        .. versionadded: 0.8.0
        """
        align = coalesce(
            self.align_option_groups,
            getattr(ctx, 'align_option_groups', None),
            default,
        )
        return cast(bool, align)

    def get_default_option_group(self, ctx: click.Context) -> OptionGroup:
        """
        .. versionadded: 0.8.0
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


def option(
    *param_decls,
    group: Optional[OptionGroup] = None,
    cls: Type[click.Option] = GroupedOption,
    **attrs
) -> OptionGroupDecorator:
    def decorator(f):
        func = click.option(*param_decls, cls=cls, **attrs)(f)
        new_option = func.__click_params__[-1]
        new_option.group = group
        if group and group.hidden:
            new_option.hidden = True
        return func

    return decorator


@overload
def option_group(
    name: str,
    help: str,
    *options: OptionDecorator,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> OptionGroupDecorator:
    ...  # pragma: no cover


@overload
def option_group(
    name: str,
    *options: OptionDecorator,
    help: Optional[str] = None,
    constraint: Optional[Constraint] = None,
    hidden: bool = False,
) -> OptionGroupDecorator:
    ...  # pragma: no cover


# noinspection PyIncorrectDocstring
def option_group(name, *args, **kwargs):
    """
    Attaches an option group to the command. This decorator is overloaded with
    two signatures::

        @option_group(name: str, *options, help: Optional[str] = None, ...)
        @option_group(name: str, help: str, *options, ...)

    In other words, if the second position argument is a string, it is interpreted
    as the "help" argument. Otherwise, it is interpreted as the first option;
    in this case, you can still pass the help as keyword argument.

    :param name: a mandatory name/title for the group
    :param help: an optional help string for the group
    :param options: option decorators like `click.option`
    :param constraint: a ``Constraint`` to validate on this option group
    :param hidden: hide this option group
    :return: a decorator that attaches the contained options to the decorated
             function
    """
    if args and isinstance(args[0], str):
        return _option_group(name, options=args[1:], help=args[0], **kwargs)
    else:
        return _option_group(name, options=args, **kwargs)


def _option_group(
    name: str,
    options: Sequence[OptionDecorator],
    hidden: bool = False,
    **kwargs,
) -> OptionGroupDecorator:
    if not options:
        raise ValueError('you must provide at least one option')

    opt_group = OptionGroup(name, **kwargs)

    def decorator(f):
        for opt_decorator in reversed(options):
            # Note: the assignment is just a precaution, as both click.option
            # and @cloup.option currently return the same f
            f = opt_decorator(f)
            new_option = f.__click_params__[-1]
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
