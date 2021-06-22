"""Tests for the "subcommand sections" feature/module."""
from textwrap import dedent

import click
import pytest
from click import pass_context

import cloup
from cloup import Section
from cloup._util import MISSING, pick_non_missing
from tests.util import new_dummy_func, pick_first_bool


@pytest.mark.parametrize(
    'align_sections', [True, False], ids=['aligned', 'non-aligned']
)
def test_subcommand_sections_are_correctly_rendered_in_help(
    runner, align_sections, get_example_group
):
    grp = get_example_group(align_sections)
    result = runner.invoke(grp, args=('--help',))
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert result.output.strip() == grp.expected_help


@pytest.mark.parametrize(
    'subcommand_cls', [click.Command, cloup.Command, click.Group, cloup.Group],
    ids=['click_Command', 'cloup_Command', 'click_Group', 'cloup_Group'],
)
@pytest.mark.parametrize(
    'assign_to_section', [True, False],
    ids=['with_section', 'without_section'],
)
def test_Group_subcommand_decorator(subcommand_cls, assign_to_section):
    grp = cloup.Group('name')
    # Use @grp.group if subcommand_class is a Group, else @grp.Command
    method_name = ('group' if issubclass(subcommand_cls, cloup.Group)
                   else 'command')
    decorator = getattr(grp, method_name)
    # Add a subcommand to the Group using the decorator
    subcommand_name = 'cmd'
    section_arg = Section('title') if assign_to_section else None
    subcommand = decorator(
        subcommand_name,
        section=section_arg,
        cls=subcommand_cls,
        help='Help'
    )(new_dummy_func())
    assert subcommand.__class__ is subcommand_cls
    assert subcommand.help == 'Help'
    assert grp.commands[subcommand_name] is subcommand
    if assign_to_section:
        section = grp._user_sections[0]
        assert section is section_arg
        assert section.commands[subcommand_name] is subcommand
    else:
        assert grp._default_section.commands[subcommand_name] is subcommand


@pytest.mark.parametrize(
    'cmd_value', [MISSING, None, True, False],
    ids=lambda val: f'cmd_{val}'
)
@pytest.mark.parametrize(
    'ctx_value', [MISSING, None, True, False],
    ids=lambda val: f'ctx_{val}'
)
def test_align_sections_context_setting(runner, ctx_value, cmd_value):
    should_align = pick_first_bool([cmd_value, ctx_value], default=True)
    cxt_settings = pick_non_missing(dict(
        align_sections=ctx_value,
        terminal_width=80,
    ))
    cmd_kwargs = pick_non_missing(dict(
        align_sections=cmd_value,
        context_settings=cxt_settings
    ))

    @cloup.group(**cmd_kwargs)
    @pass_context
    def cmd(ctx, one, much_longer_opt):
        assert cmd.must_align_sections(ctx) == should_align

    cmd.section(
        "First section",
        cloup.command('cmd', help='First command help')(new_dummy_func()),
    )

    cmd.section(
        "Second section",
        cloup.command('longer-cmd', help='Second command help')(new_dummy_func()),
    )

    result = runner.invoke(cmd, args=('--help',))
    start = result.output.find('First section')
    if should_align:
        expected = """
            First section:
              cmd         First command help

            Second section:
              longer-cmd  Second command help"""
    else:
        expected = """
            First section:
              cmd  First command help

            Second section:
              longer-cmd  Second command help"""

    expected = dedent(expected).strip()
    end = start + len(expected)
    assert result.output[start:end] == expected
