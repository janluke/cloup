"""Test for the "option groups" feature/module."""
from textwrap import dedent
from typing import cast

import click
import pytest
from click import pass_context

import cloup
from cloup import OptionGroup, option, option_group
from cloup._util import pick_non_missing, reindent
from cloup.constraints import RequireAtLeast, mutually_exclusive
from cloup.typing import MISSING
from tests.util import (make_options, new_dummy_func, parametrize, pick_first_bool)


def test_error_message_if_first_arg_is_not_a_string():
    with pytest.raises(
        TypeError, match="the first argument of `@option_group` must be its title"
    ):
        @option_group(
            option('--one'),
            option('--two'),
        )
        def f(one, two):
            pass


@parametrize(
    ['tabular_help', 'align_option_groups'],
    pytest.param(True, True, id='tabular-aligned'),
    pytest.param(True, False, id='tabular-non_aligned'),
    pytest.param(False, None, id='linear'),
)
def test_option_groups_are_correctly_displayed_in_help(
    runner, tabular_help, align_option_groups, get_example_command
):
    cmd = get_example_command(
        tabular_help=tabular_help,
        align_option_groups=align_option_groups
    )
    result = runner.invoke(cmd, args=('--help',))
    assert result.exit_code == 0
    assert result.output.strip() == cmd.expected_help


def test_option_group_constraints_are_checked(runner, get_example_command):
    cmd = get_example_command(align_option_groups=False)

    result = runner.invoke(cmd, args='arg1 --one=1')
    assert result.exit_code == 0

    result = runner.invoke(cmd, args='arg1 --one=1 --three=3 --five=4')
    assert result.exit_code == 0

    result = runner.invoke(cmd, args='arg1 --one=1 --three=3')
    assert result.exit_code == 2
    error_prefix = ('Error: when --three is set, at least 1 of the following '
                    'parameters must be set')
    assert error_prefix in result.output


def test_option_group_decorator_raises_if_group_is_passed_to_contained_option():
    with pytest.raises(ValueError):
        @option_group(
            'a group',
            cloup.option('--opt', group=OptionGroup('another group'))
        )
        def f(opt):
            pass


def test_option_group_decorator_raises_for_no_options():
    with pytest.raises(ValueError):
        cloup.option_group('grp')


@pytest.mark.parametrize(
    'cmd_value', [MISSING, None, True, False],
    ids=lambda val: f'cmd_{val}'
)
@pytest.mark.parametrize(
    'ctx_value', [MISSING, None, True, False],
    ids=lambda val: f'ctx_{val}'
)
def test_align_option_groups_context_setting(runner, ctx_value, cmd_value):
    should_align = pick_first_bool([cmd_value, ctx_value], default=True)
    cxt_settings = pick_non_missing(dict(
        align_option_groups=ctx_value,
        terminal_width=80,
    ))
    cmd_kwargs = pick_non_missing(dict(
        align_option_groups=cmd_value,
        context_settings=cxt_settings
    ))

    @cloup.command(**cmd_kwargs)
    @cloup.option_group('First group', option('--opt', help='first option'))
    @cloup.option_group('Second group', option('--much-longer-opt', help='second option'))
    @pass_context
    def cmd(ctx, one, much_longer_opt):
        assert cmd.must_align_groups(ctx) == should_align

    result = runner.invoke(cmd, args=('--help',))
    start = result.output.find('First')
    if should_align:
        expected = """
            First group:
              --opt TEXT              first option

            Second group:
              --much-longer-opt TEXT  second option

            Other options:
              --help                  Show this message and exit."""
    else:
        expected = """
            First group:
              --opt TEXT  first option

            Second group:
              --much-longer-opt TEXT  second option

            Other options:
              --help  Show this message and exit."""

    expected = dedent(expected).strip()
    end = start + len(expected)
    assert result.output[start:end] == expected


def test_context_settings_propagate_to_children(runner):
    @cloup.group(context_settings=dict(align_option_groups=False))
    def grp():
        pass

    @grp.command()
    @pass_context
    def cmd(ctx):
        assert cmd.must_align_option_groups(ctx) is False

    runner.invoke(grp, ('cmd',))


def test_that_neither_optgroup_nor_its_options_are_shown_if_optgroup_is_hidden(runner):
    @cloup.command('name')
    @cloup.option_group(
        'Hidden group',
        cloup.option('--one'),
        hidden=True
    )
    def cmd():
        pass

    result = runner.invoke(cmd, args=('--help',), catch_exceptions=False)
    assert 'Hidden group' not in result.output
    assert '--one' not in result.output


def test_that_optgroup_is_hidden_if_all_its_options_are_hidden(runner):
    @cloup.command('name')
    @cloup.option_group(
        'Hidden group',
        cloup.option('--one', hidden=True),
        cloup.option('--two', hidden=True),
    )
    def cmd():
        pass

    assert cmd.option_groups[0].hidden
    result = runner.invoke(cmd, args=('--help',), catch_exceptions=False)
    assert 'Hidden group' not in result.output


def test_option_group_options_setter_set_the_hidden_attr_of_options():
    opts = make_options('abc')
    group = OptionGroup('name')
    group.options = opts
    assert not any(opt.hidden for opt in opts)
    group.hidden = True
    group.options = opts
    assert all(opt.hidden for opt in opts)


def test_option_group_with_constrained_subgroups(runner):
    @cloup.command()
    @option_group(
        "Some options",
        RequireAtLeast(1)(
            option('-a', is_flag=True),
            option('-b', is_flag=True)
        ),
        mutually_exclusive(
            option('-c', is_flag=True),
            option('-d', is_flag=True),
        ),
        option('-e', is_flag=True),
    )
    def cmd(a, b, c, d, e):
        pass

    cmd = cast(cloup.Command, cmd)
    assert len(cmd.option_groups) == 1
    assert len(cmd.option_groups[0]) == 5

    assert runner.invoke(cmd, ['-abc']).exit_code == 0
    assert 'Error: at least 1' in runner.invoke(cmd, ['-c']).output
    assert 'mutually exclusive' in runner.invoke(cmd, ['-acd']).output

    expected_help = dedent("""
        Usage: cmd [OPTIONS]

        Some options:
          -a
          -b
          -c
          -d
          -e

        Other options:
          --help  Show this message and exit.
    """).lstrip()
    actual_help = runner.invoke(cmd, ['--help']).output
    assert actual_help == expected_help


def test_usage_of_constraints_as_decorators_inside_option_group(runner):
    @cloup.command()
    @cloup.option_group(
        "Options",
        mutually_exclusive(
            cloup.option('-a', is_flag=True),
            cloup.option('-b', is_flag=True),
            cloup.option('-c', is_flag=True),
        ),
        cloup.option('-d', is_flag=True),
    )
    def cmd(a, b, c, d):
        pass

    expected_help = dedent("""
        Usage: cmd [OPTIONS]

        Options:
          -a
          -b
          -c
          -d

        Other options:
          --help  Show this message and exit.
    """).lstrip()

    res = runner.invoke(cmd, args=['--help'])
    assert res.output == expected_help

    assert runner.invoke(cmd, args=[]).exit_code == 0
    assert runner.invoke(cmd, args='-d'.split()).exit_code == 0
    assert runner.invoke(cmd, args='-ad'.split()).exit_code == 0

    res = runner.invoke(cmd, args='-ab'.split())
    assert res.exit_code == click.UsageError.exit_code
    assert 'mutually exclusive' in res.output


def test_option_groups_raises_if_input_decorator_add_an_argument():
    with pytest.raises(
        TypeError, match='only parameter of type `Option` can be added to option groups'
    ):
        option_group(
            'Title',
            mutually_exclusive(
                cloup.argument('arg'),
                cloup.option('--opt')
            )
        )(new_dummy_func())


def test_default_option_group_title_when_the_only_other_section_is_positional_arguments(
    runner
):
    @cloup.command()
    @cloup.argument("arg", help="An argument.")
    @cloup.option("--opt", help="An option.")
    def cmd(**kwargs):
        pass

    res = runner.invoke(cmd, ["--help"])
    assert res.output == reindent("""
        Usage: cmd [OPTIONS] ARG

        Positional arguments:
          ARG         An argument.

        Options:
          --opt TEXT  An option.
          --help      Show this message and exit.
    """)
