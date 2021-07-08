import re

import click
import pytest

import cloup
from cloup._util import reindent
from tests.util import new_dummy_func


def test_command_handling_of_unknown_argument():
    with pytest.raises(TypeError, match='HINT: you set cls='):
        cloup.command(cls=click.Command, align_option_groups=True)(new_dummy_func())
    with pytest.raises(TypeError, match='nonexisting') as info:
        cloup.command(nonexisting=True)(new_dummy_func())
    assert re.search(str(info.value), 'HINT') is None


def test_group_raises_if_cls_is_not_subclass_of_click_Group():
    cloup.group()
    cloup.group(cls=click.Group)
    cloup.group(cls=cloup.Group)
    with pytest.raises(TypeError):
        cloup.group(cls=click.Command)


def test_group_handling_of_unknown_argument():
    with pytest.raises(TypeError, match='HINT'):
        cloup.group(cls=click.Group, align_sections=True)(new_dummy_func())
    with pytest.raises(TypeError) as info:
        cloup.group(unexisting_arg=True)(new_dummy_func())
    assert re.search(str(info.value), 'HINT') is None


def test_command_works_with_no_parameters(runner):
    cmd = cloup.Command(name='cmd', callback=new_dummy_func())
    res = runner.invoke(cmd, '--help')
    assert res.output == reindent("""
        Usage: cmd [OPTIONS]

        Options:
          --help  Show this message and exit.
    """)


def test_group_works_with_no_params_and_subcommands(runner):
    cmd = cloup.Group(name='cmd')
    res = runner.invoke(cmd, '--help')
    assert res.output == reindent("""
        Usage: cmd [OPTIONS] COMMAND [ARGS]...

        Options:
          --help  Show this message and exit.
    """)
