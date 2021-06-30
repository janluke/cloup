from textwrap import dedent

import click
import pytest

import cloup
from tests.util import new_dummy_func


def test_group_raises_if_cls_is_not_subclass_of_cloup_Group():
    class GroupSubclass(cloup.Group):
        pass

    # Shouldn't raise with default arguments
    cloup.group('ciao')
    cloup.group(align_sections=True, cls=cloup.Group)
    cloup.group(align_sections=True, cls=GroupSubclass)
    with pytest.raises(TypeError):
        cloup.group(cls=click.Group)


def test_command_works_with_no_parameters(runner):
    cmd = cloup.Command(name='cmd', callback=new_dummy_func())
    res = runner.invoke(cmd, '--help')
    assert res.output == dedent("""
        Usage: cmd [OPTIONS]

        Options:
          --help  Show this message and exit.
    """)[1:]


def test_group_works_with_no_params_and_subcommands(runner):
    cmd = cloup.Group(name='cmd')
    res = runner.invoke(cmd, '--help')
    assert res.output == dedent("""
        Usage: cmd [OPTIONS] COMMAND [ARGS]...

        Options:
          --help  Show this message and exit.
    """)[1:]
