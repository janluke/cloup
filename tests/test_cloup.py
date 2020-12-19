#!/usr/bin/env python
import click
import pytest
from click.testing import CliRunner

import cloup


def noop(*args, **kwargs):
    pass


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


@pytest.mark.parametrize('method_name, cls, section', [
    ('command', click.Command, None),
    ('command', cloup.Command, cloup.GroupSection('A')),
    ('group', click.Group, cloup.GroupSection('A')),
    ('group', cloup.Group, None),
])
def test_Group_command_decorator(method_name, cls, section):
    grp = cloup.Group('ciao')
    decorator = getattr(grp, method_name)
    section = cloup.GroupSection('1')
    cmd = decorator('cmd', section=section, cls=cls, help='Help')(noop)
    assert cmd.__class__ is cls
    assert grp.commands['cmd'] is cmd
    assert cmd.help == 'Help'
    if section:
        assert grp._user_sections[0].commands['cmd'] is cmd
    else:
        assert grp._default_section.commands['cmd'] is cmd


def test_option_group_decorator_raises_if_group_is_passed_to_contained_option():
    func = cloup.option_group(
        'a group', cloup.option('--opt', group=cloup.OptionGroup('another group')))
    with pytest.raises(ValueError):
        func(noop)


def test_option_group_decorator_raises_for_no_options():
    with pytest.raises(ValueError):
        cloup.option_group('grp')
