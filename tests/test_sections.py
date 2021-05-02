"""Tests for the "subcommand sections" feature/module."""

import click
import pytest

import cloup
from cloup import Section
from tests.util import noop


@pytest.mark.parametrize(
    'align_sections', [True, False], ids=['aligned', 'non-aligned']
)
def test_subcommand_sections_are_correctly_rendered_in_help(
    runner, align_sections, get_example_group
):
    grp = get_example_group(align_sections)
    result = runner.invoke(grp, args=('--help',))
    assert result.exit_code == 0
    help_text = result.output.strip()
    click_major = int(click.__version__.split('.')[0])
    if align_sections and click_major >= 8 and click.__version__ != '8.0.0a1':
        fail_reason = (
            "Click 8 fixes a minor issue with make_default_short_help() that produces a "
            "slightly different command descriptions. This test will pass starting "
            "from Cloup v0.8.0."
        )
        with pytest.xfail(fail_reason):
            assert help_text == grp.expected_help
    else:
        assert help_text == grp.expected_help


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
    )(noop)
    assert subcommand.__class__ is subcommand_cls
    assert subcommand.help == 'Help'
    assert grp.commands[subcommand_name] is subcommand
    if assign_to_section:
        section = grp._user_sections[0]
        assert section is section_arg
        assert section.commands[subcommand_name] is subcommand
    else:
        assert grp._default_section.commands[subcommand_name] is subcommand
