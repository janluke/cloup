#!/usr/bin/env python
"""
These tests are just for preventing regressions. Helps of example commands were
visually checked and they are expected to be stable. These tests just ensures
that future code changes (mostly refactoring) don't break anything.
"""
import pytest
from click.testing import CliRunner


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
