from unittest.mock import Mock

import click
import pytest
from click import Argument, Option

import cloup
from cloup import Context
from cloup._util import pick_non_missing, reindent
from cloup.constraints import (
    Constraint, RequireAtLeast, mutually_exclusive, require_all, require_one
)
from cloup.typing import MISSING
from tests.constraints.test_constraints import FakeConstraint
from tests.util import new_dummy_func, pick_first_bool


class TestConstraintMixin:
    def test_params_are_correctly_grouped_by_name(self):
        params = [
            Argument(('arg1',)),
            Option(('--str-opt',)),
            Option(('--int-opt', 'option2')),
        ]
        cmd = cloup.Command(name='cmd', params=params, callback=new_dummy_func())
        for param in params:
            assert cmd.get_param_by_name(param.name) == param

        with pytest.raises(KeyError):
            cmd.get_param_by_name('non-existing')

        assert cmd.get_params_by_name(['arg1', 'option2']) == (params[0], params[2])


@pytest.mark.parametrize('command_type', ["command", "group"])
@pytest.mark.parametrize('do_check_consistency', [
    pytest.param(True, id="with_consistency_checks"),
    pytest.param(False, id="without_consistency_checks")
])
def test_constraints_are_checked_according_to_protocol(
    runner, command_type, do_check_consistency
):
    constraints = [
        Mock(spec_set=Constraint, wraps=FakeConstraint())
        for _ in range(3)
    ]
    settings = Context.settings(check_constraints_consistency=do_check_consistency)

    command_decorator = cloup.group if command_type == "group" else cloup.command

    @command_decorator(context_settings=settings)
    @cloup.option_group('first', cloup.option('--a'), cloup.option('--b'),
                        constraint=constraints[0])
    @cloup.option_group('second', cloup.option('--c'), cloup.option('--d'),
                        constraint=constraints[1])
    @cloup.constraint(constraints[2], ['a', 'c'])
    @cloup.pass_context
    def cmd(ctx, a, b, c, d):
        assert Constraint.must_check_consistency(ctx) == do_check_consistency
        print(f'{a}, {b}, {c}, {d}')

    shell = '--a=1 --c=2'
    if isinstance(cmd, cloup.Group):
        cmd.add_command(cloup.Command(name="dummy", callback=lambda: 0))
        shell += ' dummy'

    result = runner.invoke(cmd, args=shell.split())

    assert result.output.strip() == '1, None, 2, None'
    for constr, opt_names in zip(constraints, [['a', 'b'], ['c', 'd'], ['a', 'c']]):
        opts = cmd.get_params_by_name(opt_names)
        if do_check_consistency:
            constr.check_consistency.assert_called_once_with(opts)
        else:
            constr.check_consistency.assert_not_called()
        constr.check_values.assert_called_once()


@pytest.mark.parametrize('command_type', ["command", "group"])
@pytest.mark.parametrize(
    'cmd_value', [MISSING, None, True, False],
    ids=lambda val: f'cmd_{val}'
)
@pytest.mark.parametrize(
    'ctx_value', [MISSING, None, True, False],
    ids=lambda val: f'ctx_{val}'
)
def test_constraints_are_shown_in_help_only_if_feature_is_enabled(
    runner, command_type, cmd_value, ctx_value
):
    should_show = pick_first_bool([cmd_value, ctx_value], default=False)
    cxt_settings = pick_non_missing(dict(
        show_constraints=ctx_value,
        terminal_width=80,
    ))
    cmd_kwargs = pick_non_missing(dict(
        show_constraints=cmd_value,
        context_settings=cxt_settings
    ))

    command_decorator = cloup.group if command_type == "group" else cloup.command

    @command_decorator(**cmd_kwargs)
    @cloup.option('--a')
    @cloup.option('--b')
    @cloup.option('--c')
    @cloup.constraint(FakeConstraint(help='a constraint'), ['a', 'b'])
    @cloup.constraint(FakeConstraint(help='another constraint'), ['b', 'c'])
    def cmd(a, b, c, d):
        pass

    if isinstance(cmd, cloup.Group):
        cmd.add_command(cloup.Command(name="dummy", callback=lambda: 0))

    result = runner.invoke(cmd, args=['--help'],
                           catch_exceptions=False,
                           prog_name='test')
    out = result.output

    if command_type == "group":
        if should_show:
            assert out == reindent("""
                Usage: test [OPTIONS] COMMAND [ARGS]...

                Options:
                  --a TEXT
                  --b TEXT
                  --c TEXT
                  --help    Show this message and exit.

                Constraints:
                  {--a, --b}  a constraint
                  {--b, --c}  another constraint

                Commands:
                  dummy
            """)
        else:
            assert out == reindent("""
                Usage: test [OPTIONS] COMMAND [ARGS]...

                Options:
                  --a TEXT
                  --b TEXT
                  --c TEXT
                  --help    Show this message and exit.

                Commands:
                  dummy
            """)
    else:
        base_help = reindent("""
            Usage: test [OPTIONS]

            Options:
              --a TEXT
              --b TEXT
              --c TEXT
              --help    Show this message and exit.
        """)

        if should_show:
            constraints_section = reindent("""
                Constraints:
                  {--a, --b}  a constraint
                  {--b, --c}  another constraint
            """)
            expected = base_help + "\n" + constraints_section
            assert out == expected
        else:
            assert out == base_help


def test_usage_of_constraints_as_decorators(runner):
    require_any = RequireAtLeast(1)

    @cloup.command()
    @require_any(
        cloup.argument('arg', required=False),
        cloup.option('-a'),
        cloup.option('-b'),
    )
    @mutually_exclusive(
        cloup.option('-c'),
        cloup.option('-d'),
    )
    def cmd(arg, a, b, c, d):
        pass

    assert runner.invoke(cmd, args='ARG -c CCC'.split()).exit_code == 0
    assert runner.invoke(cmd, args='-a AAA -d DDD'.split()).exit_code == 0

    res = runner.invoke(cmd, args=[])
    assert res.exit_code == click.UsageError.exit_code
    assert 'at least 1 of the following' in res.output

    res = runner.invoke(cmd, args='ARG -c CCC -d DDD'.split())
    assert res.exit_code == click.UsageError.exit_code
    assert 'mutually exclusive' in res.output


def test_group_constraints_doesnt_prevent_displaying_help_in_subcommand(runner):
    @cloup.group()
    @cloup.option_group(
        "Credentials",
        require_all(cloup.option("--user"), cloup.option("--password"))
    )
    def cli(user, password):
        """Top level group text."""

    @cli.group()
    @cloup.option_group(
        "Required",
        require_one(cloup.option("--foo"), cloup.option("--bar"))
    )
    def subgroup(foo, bar):
        """Subgroup help text."""

    @subgroup.command()
    def subcommand():
        """Subcommand help text."""

    res = runner.invoke(cli, ["subgroup", "subcommand", "--help"])
    assert res.exit_code == 0, res.output
