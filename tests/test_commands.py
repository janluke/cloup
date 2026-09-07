import re

import click
import pytest

import cloup
from cloup._util import click_version_ge_8_2, reindent
from tests.util import new_dummy_func


def test_command_handling_of_unknown_argument():
    with pytest.raises(TypeError, match='Hint: you set `cls='):
        cloup.command(cls=click.Command, align_option_groups=True)(new_dummy_func())
    with pytest.raises(TypeError, match='nonexisting') as info:
        cloup.command(nonexisting=True)(new_dummy_func())
    assert re.search(str(info.value), 'Hint') is None


def test_group_raises_if_cls_is_not_subclass_of_click_Group():
    cloup.group()
    cloup.group(cls=click.Group)
    cloup.group(cls=cloup.Group)
    with pytest.raises(TypeError):
        cloup.group(cls=click.Command)


def test_group_handling_of_unknown_argument():
    with pytest.raises(TypeError, match='Hint'):
        cloup.group(cls=click.Group, align_sections=True)(new_dummy_func())
    with pytest.raises(TypeError) as info:
        cloup.group(unexisting_arg=True)(new_dummy_func())
    assert re.search(str(info.value), 'Hint') is None


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


@pytest.mark.parametrize('command_cls, reference_cls', [
    (cloup.Command, click.Command),
    (cloup.Group, click.Group),
])
@pytest.mark.parametrize('help_text', [
    None, '', 'Do a thing.', 'First paragraph.\n\nSecond paragraph.\fHidden text.',
])
@pytest.mark.parametrize('deprecated', [False, True, '', 'use `newcmd` instead'])
def test_deprecated_command_help_matches_click(
    runner, command_cls, reference_cls, help_text, deprecated,
):
    cmd = command_cls(name='example', help=help_text, deprecated=deprecated)
    reference = reference_cls(name='example', help=help_text, deprecated=deprecated)

    result = runner.invoke(cmd, ['--help'], terminal_width=80)
    expected = runner.invoke(reference, ['--help'], terminal_width=80)

    assert result.exit_code == expected.exit_code == 0
    # Older Click 8.2 releases add an extra space before a standalone label.
    expected_output = expected.output.replace('\n   (DEPRECATED', '\n  (DEPRECATED')
    assert result.output == expected_output


@pytest.mark.skipif(not click_version_ge_8_2, reason='requires Click 8.2 or newer')
def test_deprecated_command_help_keeps_theme(runner):
    @cloup.command(
        deprecated='use `newcmd` instead',
        formatter_settings={'theme': cloup.HelpTheme(
            command_help=cloup.Style(fg='yellow'),
        )},
    )
    def example():
        """Do a thing."""

    result = runner.invoke(example, ['--help'], color=True)
    assert result.exit_code == 0
    assert click.style('Do a thing. (DEPRECATED: use `newcmd` instead)', fg='yellow') \
        in result.output


class TestDidYouMean:
    @staticmethod
    @pytest.fixture(scope="class")
    def cmd():
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


def test_group_command_class_is_used_to_create_subcommands(runner):
    class CustomCommand(cloup.Command):

        def __init__(self, *args, **kwargs):
            kwargs.setdefault("context_settings", {"help_option_names": ("--help", "-h")})
            super().__init__(*args, **kwargs)

    class CustomGroup(cloup.Group):
        command_class = CustomCommand

    @cloup.group("cli", cls=CustomGroup)
    def my_cli():
        pass

    @my_cli.command()
    def subcommand():
        pass

    assert isinstance(subcommand, CustomCommand)

    res = runner.invoke(my_cli, ["subcommand", "--help"])
    assert res.output == reindent("""
        Usage: cli subcommand [OPTIONS]

        Options:
          -h, --help  Show this message and exit.
    """)


def test_group_class_is_used_to_create_subgroups(runner):
    class CustomGroup(cloup.Group):
        group_class = type

    class OtherCustomGroup(cloup.Group):
        group_class = cloup.Group

    @cloup.group("cli", cls=CustomGroup)
    def my_cli():
        pass

    @my_cli.group()
    def sub_group():
        pass

    @my_cli.group(cls=OtherCustomGroup)
    def other_group():
        pass

    @other_group.group()
    def other_sub_group():
        pass

    assert isinstance(sub_group, CustomGroup)
    assert isinstance(other_group, OtherCustomGroup)
    assert isinstance(other_sub_group, cloup.Group)
