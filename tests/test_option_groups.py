"""Tests for the "option groups" feature/module."""
import pytest

import cloup
from tests.util import noop


def test_option_group_decorator_raises_if_group_is_passed_to_contained_option():
    func = cloup.option_group(
        'a group', cloup.option('--opt', group=cloup.OptionGroup('another group')))
    with pytest.raises(ValueError):
        func(noop)


def test_option_group_decorator_raises_for_no_options():
    with pytest.raises(ValueError):
        cloup.option_group('grp')


@pytest.mark.parametrize(
    'align_option_groups', [True, False], ids=['aligned', 'non-aligned']
)
def test_option_groups_are_correctly_displayed_in_help(
    runner, align_option_groups, get_example_command
):
    cmd = get_example_command(align_option_groups)
    result = runner.invoke(cmd, args=('--help',))
    assert result.exit_code == 0
    assert result.output.strip() == cmd.expected_help
