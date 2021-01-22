from unittest.mock import Mock

import click
import pytest
from click import Argument, Option

import cloup
from cloup import ConstraintMixin
from cloup.constraints import Constraint
from tests.util import noop


class TestConstraintMixin:
    def test_params_are_correctly_grouped_by_name(self):
        class Cmd(ConstraintMixin, click.Command):
            pass

        params = [
            Argument(('arg1',)),
            Option(('--opt1',)),
            Option(('--opt2', 'option2')),
        ]
        cmd = Cmd(name='cmd', params=params, callback=noop)
        for param in params:
            assert cmd.get_param_by_name(param.name) == param

        with pytest.raises(KeyError):
            cmd.get_param_by_name('non-existing')

        assert cmd.get_params_by_name(['arg1', 'option2']) == [params[0], params[2]]

    def test_option_group_constraints_are_checked(self, runner):
        constraints = [Mock(Constraint), Mock(Constraint)]

        @cloup.command()
        @cloup.option_group('first', cloup.option('-a'), cloup.option('-b'),
                            constraint=constraints[0])
        @cloup.option_group('second', cloup.option('-c'), cloup.option('-d'),
                            constraint=constraints[1])
        def cmd(**kwargs):
            print('okay')

        result = runner.invoke(cmd, args=('-a', '1', '-c', '2'))
        assert result.exit_code == 0
        assert result.output.strip() == 'okay'
        for constraint, opt_names in zip(constraints, [['a', 'b'], ['c', 'd']]):
            assert constraint.check.call_count == 1
