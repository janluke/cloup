from typing import Callable, Optional, Sequence, Type, overload

import click

#: A decorator that registers one or multiple click Options to the decorated function
OptionDecorator = Callable[[Callable], Callable]


class OptionGroup:
    def __init__(self, name: str, help: Optional[str] = None):
        if not name:
            raise ValueError('name is a mandatory argument')
        self.name = name
        self.help = help
        self.options = []  # type: Sequence[click.Option]

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
def option_group(name: str, help: str, *options) -> OptionDecorator:
    ...


@overload
def option_group(name: str, *options, help: Optional[str] = None) -> OptionDecorator:
    ...


def option_group(name: str, *args, **kwargs) -> OptionDecorator:
    """
    Attaches an option group to the command. This decorator is overloaded with
    two signatures::

        @option_group(name: str, *options, help: Optional[str] = None)
        @option_group(name: str, help: str, *options)

    In other words, if the second position argument is a string, it is interpreted
    as the "help" argument. Otherwise, it is interpreted as the first option;
    in this case, you can still pass the help as keyword argument.
    """
    if args and isinstance(args[0], str):
        return _option_group(name, options=args[1:], help=args[0])
    else:
        return _option_group(name, options=args, **kwargs)


def _option_group(
    name: str, options: Sequence[Callable], help: Optional[str] = None
) -> OptionDecorator:
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
