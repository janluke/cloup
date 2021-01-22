from unittest.mock import Mock

import click
from click import Command, Context
from pytest import fixture

import cloup


@fixture()
def dummy_ctx() -> Context:
    """Useful for testing methods that needs a Context but don't actually use it."""
    return Mock(Context)


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
    @cloup.option('--opt1')
    @cloup.option('--opt2')
    @cloup.option('--opt3')
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

    return f
