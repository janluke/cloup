#!/usr/bin/env python
import click
import pytest
from click.testing import CliRunner

import cloup
from cloup import Section
from .util import noop


@pytest.mark.parametrize('align_option_groups', [True, False], ids=['aligned', 'non-aligned'])
def test_example_command_help(align_option_groups, get_example_command):
    cmd = get_example_command(align_option_groups)
    runner = CliRunner()
    result = runner.invoke(cmd, args=('--help',))
    assert result.exit_code == 0
    assert result.output.strip() == cmd.expected_help


@pytest.mark.parametrize('align_sections', [True, False], ids=['aligned', 'non-aligned'])
def test_example_group_help(align_sections, get_example_group):
    grp = get_example_group(align_sections)
    result = CliRunner().invoke(grp, args=('--help',))
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert result.output.strip() == grp.expected_help


@pytest.mark.parametrize('subcommand_cls', [
    click.Command, cloup.Command,  click.Group, cloup.Group
], ids=['click_Command', 'cloup_Command', 'click_Group', 'cloup_Group'])
@pytest.mark.parametrize('assign_to_section', [True, False])
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


def test_option_group_decorator_raises_if_group_is_passed_to_contained_option():
    func = cloup.option_group(
        'a group', cloup.option('--opt', group=cloup.OptionGroup('another group')))
    with pytest.raises(ValueError):
        func(noop)


def test_option_group_decorator_raises_for_no_options():
    with pytest.raises(ValueError):
        cloup.option_group('grp')
