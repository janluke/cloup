from contextlib import contextmanager
from typing import Iterable, List

import pytest
from click import Command, Context, Option

import cloup


def noop(*args, **kwargs):
    pass


def flag_opt(*param_decl):
    return Option(param_decl, is_flag=True)


def multi_opt(*param_decl):
    return Option(param_decl, multiple=True)


def mark_parametrize(argnames, *argvalues, **kwargs):
    return pytest.mark.parametrize(argnames, argvalues, **kwargs)


def make_context(cmd: Command, shell: str) -> Context:
    args = shell.split()
    return cmd.make_context(cmd.name, args)


def make_fake_context(
    params: Iterable[str],
    command_cls=cloup.Command,
) -> Context:
    """Creates an simple instance of Command with the specified parameters,
    then create a fake context without actually invoke the command."""
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
