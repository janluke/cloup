from contextlib import contextmanager
from typing import Iterable, List
from unittest.mock import Mock

import pytest
from click import Command, Context, Option

import cloup


def noop(*args, **kwargs):
    pass


def int_opt(*args, **kwargs):
    return Option(*args, type=int, **kwargs)


def bool_opt(*args, **kwargs):
    return Option(*args, type=bool, **kwargs)


def flag_opt(*args, **kwargs):
    return Option(*args, is_flag=True, **kwargs)


def multi_opt(*args, **kwargs):
    return Option(*args, multiple=True, **kwargs)


def tuple_opt(*args, **kwargs):
    return Option(*args, nargs=3, **kwargs)


def parametrize(argnames, *argvalues, **kwargs):
    return pytest.mark.parametrize(argnames, argvalues, **kwargs)


def make_context(cmd: Command, shell: str) -> Context:
    args = shell.split()
    return cmd.make_context(cmd.name, args)


def make_fake_context(
    params: Iterable[str],
    command_cls=cloup.Command,
) -> Context:
    """Creates a simple instance of Command with the specified parameters,
    then create a fake context without actually invoking the command."""
    return Context(command_cls('fake', params=params, callback=noop))


def make_options(names: Iterable[str], **common_kwargs) -> List[Option]:
    return [Option([f'--{name}'], **common_kwargs) for name in names]


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
