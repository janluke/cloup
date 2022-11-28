from contextlib import contextmanager
from typing import Iterable, List
from unittest.mock import Mock

import click
import pytest

import cloup
from cloup import Context


def pick_first_bool(args: Iterable, *, default: bool) -> bool:
    return next((arg for arg in args if isinstance(arg, bool)), default)


def new_dummy_func():
    return lambda *args, **kwargs: 1


def int_opt(*args, **kwargs):
    return click.Option(*args, type=int, **kwargs)


def bool_opt(*args, **kwargs):
    return click.Option(*args, type=bool, **kwargs)


def flag_opt(*args, **kwargs):
    return click.Option(*args, is_flag=True, **kwargs)


def multi_opt(*args, **kwargs):
    return click.Option(*args, multiple=True, **kwargs)


def tuple_opt(*args, **kwargs):
    return click.Option(*args, nargs=3, **kwargs)


def parametrize(argnames, *argvalues, **kwargs):
    return pytest.mark.parametrize(argnames, argvalues, **kwargs)


def make_context(cmd: click.Command, shell: str) -> click.Context:
    args = shell.split()
    return cmd.make_context(cmd.name, args)


def make_fake_context(
    params: Iterable[click.Parameter],
    command_cls=cloup.Command,
    cls=Context,
    **ctx_kwargs
) -> Context:
    """Create a simple instance of Command with the specified parameters,
    then create a fake context without actually invoking the command."""
    return cls(
        command_cls('fake', params=params, callback=new_dummy_func()), **ctx_kwargs
    )


def make_options(names: Iterable[str], **common_kwargs) -> List[click.Option]:
    return [click.Option([f'--{name}'], **common_kwargs) for name in names]


def should_raise(expected_exception, *, when, **kwargs):
    if when:
        return pytest.raises(expected_exception, **kwargs)

    @contextmanager
    def manager():
        yield

    return manager()


def mock_repr(value, *args, **kwargs):
    m = Mock(*args, **kwargs)
    m.__repr__ = lambda x: value
    return m
