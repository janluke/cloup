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


class TestDidYouMean:
    @pytest.fixture(scope="class")
    def cmd(self):
        cmd = cloup.Group(name="cmd")
        subcommands = [
            ('install', ['ins']),
            ('remove', ['rm']),
            ('clear', [])
        ]
        for name, aliases in subcommands:
            cmd.add_command(
                cloup.Command(name=name, aliases=aliases, callback=new_dummy_func()))
        return cmd

    def test_with_no_matches(self, runner, cmd):
        res = runner.invoke(cmd, 'asdfdsgdfgdf')
        assert res.output == reindent("""
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'asdfdsgdfgdf'.
        """)

    def test_with_one_match(self, runner, cmd):
        res = runner.invoke(cmd, 'clearr')
        assert res.output == reindent("""
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'clearr'. Did you mean 'clear'?
        """)

    def test_with_multiple_matches(self, runner, cmd):
        res = runner.invoke(cmd, 'inst')
        assert res.output == reindent("""
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'inst'. Did you mean one of these?
               ins
               install
        """)


@pytest.mark.parametrize("decorator", [cloup.command, cloup.group])
def test_error_is_raised_when_command_decorators_are_used_without_parenthesis(decorator):
    with pytest.raises(Exception, match="parenthesis"):
        @decorator
        def cmd():
            pass


def test_error_is_raised_when_group_subcommand_decorators_are_used_without_parenthesis():
    @cloup.group()
    def root():
        pass

    with pytest.raises(Exception, match="parenthesis"):
        @root.group
        def subgroup():
            pass

    with pytest.raises(Exception, match="parenthesis"):
        @root.command
        def subcommand():
            pass
