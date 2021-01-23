"""
Implements support to option group.
"""
from collections import defaultdict
from typing import Callable, List, Optional, Sequence, Tuple, Type, TypeVar, overload

import click

from click import Option, Parameter

C = TypeVar('C', bound=Callable)

#: A decorator that registers an option to the wrapped function
OptionDecorator = Callable[[C], C]

#: A decorator that registers an option group to the wrapped function
OptionGroupDecorator = Callable[[C], C]


class OptionGroup:
    def __init__(self, name: str, help: Optional[str] = None):
        if not name:
            raise ValueError('name is a mandatory argument')
        self.name = name
        self.help = help
        self.options: Sequence[click.Option] = []

    def get_help_records(self, ctx: click.Context):
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
        return 'OptionGroup({!r}, help={!r}, options={})'.format(
            self.name, self.help, self.options)

    def __str__(self) -> str:
        return 'OptionGroup({!r}, help={!r}, options={})'.format(
            self.name, self.help, [opt.name for opt in self.options])


class GroupedOption(click.Option):
    """ A click.Option with an extra field ``group`` of type OptionGroup """

    def __init__(self, *args, group: Optional[OptionGroup] = None, **attrs):
        super().__init__(*args, **attrs)
        self.group = group


def has_option_group(param) -> bool:
    return hasattr(param, 'group') and param.group is not None


def get_option_group_of(param, default=None):
    return param.group if has_option_group(param) else default


class OptionGroupMixin:
    """Implements support to option groups.

    .. versionadded:: 0.5.0
    """

    def __init__(self, *args, align_option_groups: bool = True, **kwargs):
        self.align_option_groups = align_option_groups
        self.option_groups, self.ungrouped_options = \
            self._option_groups_from_params(kwargs['params'])
        if len(self.__class__.__mro__) > 1:
            # This "if" allows using this class as "stand-alone" class
            super().__init__(*args, **kwargs)   # type: ignore

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

    def format_option_group(self, ctx: click.Context,
                            formatter: click.HelpFormatter,
                            option_group: OptionGroup,
                            help_records: Optional[Sequence] = None):
        if help_records is None:
            help_records = option_group.get_help_records(ctx)
        if not help_records:
            return
        with formatter.section(option_group.name):
            if option_group.help:
                formatter.write_text(option_group.help)
            formatter.write_dl(help_records)

    def format_options(self, ctx: click.Context,
                       formatter: click.HelpFormatter,
                       max_option_width: int = 30):
        records_by_group = {}
        for group in self.option_groups:
            records_by_group[group] = group.get_help_records(ctx)
        ungrouped_options = self.get_ungrouped_options(ctx)
        if ungrouped_options:
            default_group = OptionGroup('Other options' if records_by_group else 'Options')
            default_group.options = ungrouped_options
            records_by_group[default_group] = default_group.get_help_records(ctx)

        if self.align_option_groups:
            option_name_width = min(
                max_option_width,
                max(len(rec[0])
                    for records in records_by_group.values()
                    for rec in records)
            )
            # This is a hacky way to have aligned options groups.
            # Pad the first column of the first entry of each group to reach option_name_width
            for records in records_by_group.values():
                first = records[0]
                pad_width = option_name_width - len(first[0])
                if pad_width <= 0:
                    continue
                records[0] = (first[0] + ' ' * pad_width, first[1])

        for group, records in records_by_group.items():
            self.format_option_group(ctx, formatter, group, help_records=records)


def option(
    *param_decls,
    group: Optional[OptionGroup] = None,
    cls: Type[click.Option] = GroupedOption,
    **attrs
) -> OptionDecorator:
    def decorator(f):
        func = click.option(*param_decls, cls=cls, **attrs)(f)
        new_option = func.__click_params__[-1]
        new_option.group = group
        return func

    return decorator


@overload
def option_group(
    name: str,
    help: str,
    *options: OptionDecorator,
) -> OptionGroupDecorator:
    ...  # pragma: no cover


@overload
def option_group(
    name: str,
    *options: OptionDecorator,
    help: Optional[str] = None,
) -> OptionGroupDecorator:
    ...  # pragma: no cover


def option_group(name: str, *args, **kwargs) -> OptionDecorator:
    """
    Attaches an option group to the command. This decorator is overloaded with
    two signatures::

        @option_group(name: str, *options, help: Optional[str] = None)
        @option_group(name: str, help: str, *options)

    In other words, if the second position argument is a string, it is interpreted
    as the "help" argument. Otherwise, it is interpreted as the first option;
    in this case, you can still pass the help as keyword argument.

    :param name: a mandatory name/title for the group
    :param help: an optional help string for the group
    :param options: option decorators like `click.option`
    :return: a decorator that attaches the contained options to the decorated
             function (by monkey-patching it)
    """
    if args and isinstance(args[0], str):
        return _option_group(name, options=args[1:], help=args[0])
    else:
        return _option_group(name, options=args, **kwargs)


def _option_group(
    name: str, options: Sequence[OptionDecorator], help: Optional[str] = None
) -> OptionGroupDecorator:
    if not options:
        raise ValueError('you must provide at least one option')

    opt_group = OptionGroup(name, help=help)

    def decorator(f):
        for opt_decorator in reversed(options):
            # Note: the assignment is just a precaution, as both click.option
            # and @cloup.option currently return the same f
            f = opt_decorator(f)
            new_option = f.__click_params__[-1]
            curr_group = get_option_group_of(new_option)
            if curr_group is not None:
                raise ValueError(
                    'option {} was first assigned to {} and then passed '
                    'as argument to @option_group({!r}, ...)'
                    .format(new_option.opts, curr_group, name))
            new_option.group = opt_group
        return f

    return decorator
