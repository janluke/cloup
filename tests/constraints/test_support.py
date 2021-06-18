import textwrap
from unittest.mock import Mock

import click
import pytest
from click import Argument, Option

import cloup
from cloup import ConstraintMixin, Context
from cloup.constraints import Constraint
from tests.constraints.test_constraints import FakeConstraint
from tests.util import NOT_PROVIDED, noop, pick_first_bool, pick_provided


class Cmd(ConstraintMixin, click.Command):
    pass


class TestConstraintMixin:
    def test_params_are_correctly_grouped_by_name(self):
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

        assert cmd.get_params_by_name(['arg1', 'option2']) == (params[0], params[2])


@pytest.mark.parametrize(
    'do_check_consistency', [True, False],
    ids=['with_consistency_checks', 'without_consistency_checks']
)
def test_constraints_are_checked_according_to_protocol(runner, do_check_consistency):
    constraints = [
        Mock(spec_set=Constraint, wraps=FakeConstraint()),
        Mock(spec_set=Constraint, wraps=FakeConstraint()),
        Mock(spec_set=Constraint, wraps=FakeConstraint()),
    ]
    settings = Context.settings(check_constraints_consistency=do_check_consistency)

    @cloup.command(context_settings=settings)
    @cloup.option_group('first', cloup.option('--a'), cloup.option('--b'),
                        constraint=constraints[0])
    @cloup.option_group('second', cloup.option('--c'), cloup.option('--d'),
                        constraint=constraints[1])
    @cloup.constraint(constraints[2], ['a', 'c'])
    @cloup.pass_context
    def cmd(ctx, a, b, c, d):
        assert Constraint.must_check_consistency(ctx) == do_check_consistency
        print(f'{a}, {b}, {c}, {d}')

    result = runner.invoke(cmd, args='--a=1 --c=2'.split())

    assert result.output.strip() == '1, None, 2, None'
    for constr, opt_names in zip(constraints, [['a', 'b'], ['c', 'd'], ['a', 'c']]):
        opts = cmd.get_params_by_name(opt_names)
        if do_check_consistency:
            constr.check_consistency.assert_called_once_with(opts)
        else:
            constr.check_consistency.assert_not_called()
        constr.check_values.assert_called_once()


@pytest.mark.parametrize(
    'cmd_value', [NOT_PROVIDED, None, True, False],
    ids=lambda val: f'cmd_{val}'
)
@pytest.mark.parametrize(
    'ctx_value', [NOT_PROVIDED, None, True, False],
    ids=lambda val: f'ctx_{val}'
)
def test_constraints_are_shown_in_help_only_if_feature_is_enabled(
    runner, cmd_value, ctx_value
):
    should_show = pick_first_bool([cmd_value, ctx_value], default=False)
    cxt_settings = pick_provided(
        show_constraints=ctx_value,
        terminal_width=80,
    )
    cmd_kwargs = pick_provided(
        show_constraints=cmd_value,
        context_settings=cxt_settings
    )

    @cloup.command(**cmd_kwargs)
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

    if should_show:
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
