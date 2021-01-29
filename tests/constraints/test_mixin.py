from unittest.mock import Mock

import click
import pytest
from click import Argument, Option
from pytest import mark

import cloup
from cloup import ConstraintMixin
from cloup.constraints import Constraint
from tests.constraints.test_constraints import FakeConstraint
from tests.util import noop


class TestConstraintMixin:
    def test_params_are_correctly_grouped_by_name(self):
        class Cmd(ConstraintMixin, click.Command):
            pass

        params = [
            Argument(('arg1',)),
            Option(('--str-opt',)),
            Option(('--int-opt', 'option2')),
        ]
        cmd = Cmd(name='cmd', params=params, callback=noop)
        for param in params:
            assert cmd.get_param_by_name(param.name) == param

        with pytest.raises(KeyError):
            cmd.get_param_by_name('non-existing')

        assert cmd.get_params_by_name(['arg1', 'option2']) == [params[0], params[2]]

    @mark.parametrize(
        'do_check_consistency', [True, False],
        ids=['consistency', 'no_consistency']
    )
    def test_option_group_constraints_are_checked(self, runner, do_check_consistency):
        constraints = [
            Mock(spec_set=Constraint, wraps=FakeConstraint()),
            Mock(spec_set=Constraint, wraps=FakeConstraint())
        ]

        @cloup.command()
        @cloup.option_group('first', cloup.option('--a'), cloup.option('--b'),
                            constraint=constraints[0])
        @cloup.option_group('second', cloup.option('--c'), cloup.option('--d'),
                            constraint=constraints[1])
        def cmd(a, b, c, d):
            print(f'{a}, {b}, {c}, {d}')

        with Constraint.consistency_checks_toggled(do_check_consistency):
            assert Constraint.must_check_consistency() == do_check_consistency
            result = runner.invoke(cmd, args='--a=1 --c=2'.split(), catch_exceptions=False)

        assert result.output.strip() == '1, None, 2, None'
        for constr, opt_names in zip(constraints, [['a', 'b'], ['c', 'd']]):
            opts = cmd.get_params_by_name(opt_names)
            if do_check_consistency:
                constr.check_consistency.assert_called_once_with(opts)
            else:
                constr.check_consistency.assert_not_called()
            constr.check_values.assert_called_once()
