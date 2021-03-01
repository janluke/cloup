import textwrap
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
    def test_constraints_are_checked(self, runner, do_check_consistency):
        constraints = [
            Mock(spec_set=Constraint, wraps=FakeConstraint()),
            Mock(spec_set=Constraint, wraps=FakeConstraint()),
            Mock(spec_set=Constraint, wraps=FakeConstraint()),
        ]

        @cloup.command()
        @cloup.option_group('first', cloup.option('--a'), cloup.option('--b'),
                            constraint=constraints[0])
        @cloup.option_group('second', cloup.option('--c'), cloup.option('--d'),
                            constraint=constraints[1])
        @cloup.constraint(constraints[2], ['a', 'c'])
        def cmd(a, b, c, d):
            print(f'{a}, {b}, {c}, {d}')

        with Constraint.consistency_checks_toggled(do_check_consistency):
            assert Constraint.must_check_consistency() == do_check_consistency
            result = runner.invoke(cmd, args='--a=1 --c=2'.split(),
                                   catch_exceptions=False)

        assert result.output.strip() == '1, None, 2, None'
        for constr, opt_names in zip(constraints, [['a', 'b'], ['c', 'd'], ['a', 'c']]):
            opts = cmd.get_params_by_name(opt_names)
            if do_check_consistency:
                constr.check_consistency.assert_called_once_with(opts)
            else:
                constr.check_consistency.assert_not_called()
            constr.check_values.assert_called_once()

    @mark.parametrize(
        'show_constraints', [True, False],
        ids=['enabled', 'disabled']
    )
    def test_constraints_are_showed_in_help_only_if_enabled(
        self, runner, show_constraints
    ):
        @cloup.command(show_constraints=show_constraints,
                       context_settings={'terminal_width': 80})
        @cloup.option('--a')
        @cloup.option('--b')
        @cloup.option('--c')
        @cloup.constraint(FakeConstraint(help='a constraint'), ['a', 'b'])
        @cloup.constraint(FakeConstraint(help='another constraint'), ['b', 'c'])
        def cmd(a, b, c, d):
            pass

        result = runner.invoke(cmd, args=['--help'],
                               catch_exceptions=False,
                               prog_name='test')
        out = result.output.strip()

        if show_constraints:
            expected = textwrap.dedent('''
                Usage: test [OPTIONS]

                Options:
                  --a TEXT
                  --b TEXT
                  --c TEXT
                  --help    Show this message and exit.

                Constraints:
                  {--a, --b}  a constraint
                  {--b, --c}  another constraint
            ''').strip()
            assert out == expected
        else:
            expected = textwrap.dedent('''
                Usage: test [OPTIONS]

                Options:
                  --a TEXT
                  --b TEXT
                  --c TEXT
                  --help    Show this message and exit.
            ''').strip()
            assert out == expected
