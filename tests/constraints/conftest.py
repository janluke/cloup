from typing import cast
from unittest.mock import Mock

import click
from click import Context
from pytest import fixture

import cloup
from cloup import Command


@fixture()
def dummy_ctx():
    """Useful for testing methods that needs a Context but don't actually use it."""
    dummy = Mock(spec_set=Context(Command('name', params=[])))
    dummy.command.__class__ = Command
    return dummy


@fixture()
def sample_cmd() -> Command:
    """Useful for testing constraints against a variety of parameter kinds.
    Parameters have names that should make easy to remember their "kind"
    without the need for looking up this code."""
    @cloup.command()
    # Optional arguments
    @click.argument('arg1', required=False)
    @click.argument('arg2', required=False)
    # Plain options without default
    @cloup.option('--str-opt')
    @cloup.option('--int-opt', type=int)
    @cloup.option('--bool-opt', type=bool)
    # Flags
    @cloup.option('--flag / --no-flag')
    @cloup.option('--flag2', is_flag=True)
    # Options with default
    @cloup.option('--def1', default=1)
    @cloup.option('--def2', default=2)
    # Options that take a tuple
    @cloup.option('--tuple', nargs=2, type=int)
    # Options that can be specified multiple times
    @cloup.option('--mul1', type=int, multiple=True)
    @cloup.option('--mul2', type=int, multiple=True)
    def f(**kwargs):
        print('It works')

    return cast(Command, f)
