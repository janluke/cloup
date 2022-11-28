from functools import partial
from typing import Sequence
from unittest import mock
from unittest.mock import Mock

import click
import pytest
from click import Command, Context, Parameter
from pytest import mark

from cloup.constraints import (
    AcceptAtMost,
    AcceptBetween,
    Constraint,
    ErrorFmt,
    Rephraser,
    RequireAtLeast,
    RequireExactly,
    require_all,
)
from cloup.constraints.exceptions import ConstraintViolated, UnsatisfiableConstraint
from tests.util import (
    make_context, make_fake_context, make_options, parametrize, should_raise
)


class FakeConstraint(Constraint):
    """Sometimes it's useful to use

        Mock(wraps=FakeConstraint(...))

    to create a test double with characteristics of both a mock and a fake."""

    def __init__(self, satisfied=True, consistent=True, help='help',
                 error='error', inconsistency_reason='consistency_error'):
        self.satisfied = satisfied
        self.consistent = consistent
        self._help = help
        self.error = error
        self.inconsistency_reason = inconsistency_reason
        self.check_consistency_calls = []
        self.check_values_calls = []

    def help(self, ctx: Context) -> str:
        return self._help

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        self.check_consistency_calls.append(dict(params=params))
        if not self.consistent:
            raise UnsatisfiableConstraint(self, params, self.inconsistency_reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        self.check_values_calls.append(dict(params=params, ctx=ctx))
        if not self.satisfied:
            raise ConstraintViolated(self.error, ctx=ctx, constraint=self, params=params)


class TestBaseConstraint:
    def test_rephrased_calls_Rephraser_correctly(self):
        with mock.patch('cloup.constraints._core.Rephraser') as rephraser_cls:
            cons = FakeConstraint()
            cons.rephrased(help='ciao')
            rephraser_cls.assert_called_with(cons, help='ciao', error=None)
            cons.rephrased(error='ciao')
            rephraser_cls.assert_called_with(cons, help=None, error='ciao')

    def test_hidden_constraint_returns_empty_help(self, dummy_ctx):
        hidden = FakeConstraint(help='non-empty help').hidden()
        assert isinstance(hidden, Rephraser)
        assert hidden.help(dummy_ctx) == ''

    @mark.parametrize('satisfied', [True, False])
    @mark.parametrize('consistent', [True, False])
    def test__call__raises_iff_check_raises(self, satisfied, consistent):
        ctx = make_fake_context(make_options('abc'))
        cons = FakeConstraint(satisfied=satisfied, consistent=consistent)
        exc_class = UnsatisfiableConstraint if not consistent else ConstraintViolated
        with should_raise(exc_class, when=not (consistent and satisfied)):
            cons.check(['a', 'b'], ctx)

    @parametrize(
        ['ctx_kwargs', 'should_check'],
        pytest.param(dict(cls=click.Context), True, id='click.Context [no setting]'),
        pytest.param(dict(), True, id='cloup.Context [default]'),
        pytest.param(dict(check_constraints_consistency=False), False, id='disabled'),
    )
    def test_check_consistency_is_called_unless_disabled(self, ctx_kwargs, should_check):
        ctx = make_fake_context(make_options('abc'), **ctx_kwargs)
        constr = FakeConstraint()
        constr.check(['a', 'b'], ctx)
        assert Constraint.must_check_consistency(ctx) == should_check
        assert len(constr.check_consistency_calls) == int(should_check)

    def test_error_is_raised_when_using_call_the_old_way(self):
        constr = FakeConstraint()
        with pytest.raises(TypeError, match='since Cloup v0.9, calling a constraint'):
            constr(['a', 'b'])


class TestAnd:

    @mark.parametrize('b_satisfied', [False, True])
    @mark.parametrize('a_satisfied', [False, True])
    def test_check(self, a_satisfied, b_satisfied):
        ctx = make_fake_context(make_options(['arg1', 'str_opt', 'int_opt', 'flag']))
        a = FakeConstraint(satisfied=a_satisfied)
        b = FakeConstraint(satisfied=b_satisfied)
        c = a & b
        with should_raise(ConstraintViolated, when=not (a_satisfied and b_satisfied)):
            c.check(params=['arg1', 'str_opt'], ctx=ctx)

    def test_operand_merging(self):
        a, b, c, d = (FakeConstraint() for _ in range(4))
        res = (a & b) & c
        assert res.constraints == (a, b, c)
        res = (a & b) & (c & d)
        assert res.constraints == (a, b, c, d)
        res = (a & b) & (c | d)
        assert len(res.constraints) == 3


class TestOr:
    @mark.parametrize('b_satisfied', [False, True])
    @mark.parametrize('a_satisfied', [False, True])
    def test_check(self, a_satisfied, b_satisfied):
        ctx = make_fake_context(make_options(['arg1', 'str_opt', 'int_opt', 'flag']))
        a = FakeConstraint(satisfied=a_satisfied)
        b = FakeConstraint(satisfied=b_satisfied)
        c = a | b
        with should_raise(ConstraintViolated, when=not (a_satisfied or b_satisfied)):
            c.check(params=['arg1', 'str_opt'], ctx=ctx)

    def test_operands_merging(self):
        a, b, c, d = (FakeConstraint() for _ in range(4))
        res = (a | b) | c
        assert res.constraints == (a, b, c)
        res = (a | b) | (c | d)
        assert res.constraints == (a, b, c, d)
        res = (a | b) | (c & d)
        assert len(res.constraints) == 3


def test_operator_help(dummy_ctx):
    ctx = dummy_ctx
    a, b, c = RequireAtLeast(3), AcceptAtMost(10), RequireExactly(8)
    a_help, b_help, c_help = (cons.help(ctx) for cons in [a, b, c])
    assert (a | b | c).help(ctx) == f'{a_help} or {b_help} or {c_help}'
    assert (a | b & c).help(ctx) == f'{a_help} or ({b_help} and {c_help})'


class TestRequireAtLeast:
    def test_init_raises_for_invalid_n(self):
        RequireAtLeast(0)
        with pytest.raises(ValueError):
            RequireAtLeast(-1)

    def test_help(self, dummy_ctx):
        assert '3' in RequireAtLeast(3).help(dummy_ctx)

    def test_check_consistency(self):
        check_consistency = RequireAtLeast(3).check_consistency
        check_consistency(make_options('abc'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('ab'))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0')
        check = partial(RequireAtLeast(2).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'def1'])  # arg1 and def1
        check(['arg1', 'str_opt', 'def1'])  # arg1, str-opt and def1
        with pytest.raises(ConstraintViolated):
            check(['str_opt', 'arg2', 'flag'])  # only str-opt is set


class TestAcceptAtMost:
    def test_init_raises_for_invalid_n(self):
        AcceptAtMost(0)
        with pytest.raises(ValueError):
            AcceptAtMost(-1)

    def test_help(self, dummy_ctx):
        assert '3' in AcceptAtMost(3).help(dummy_ctx)

    def test_check_consistency(self):
        check_consistency = AcceptAtMost(2).check_consistency
        check_consistency(make_options('abc'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('abc', required=True))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0')
        check = partial(AcceptAtMost(2).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'flag'])  # arg1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'str_opt', 'def1'])  # arg1, str-opt, def1


class TestRequireExactly:
    def test_init_raises_for_invalid_n(self):
        with pytest.raises(ValueError):
            RequireExactly(0)
        with pytest.raises(ValueError):
            RequireExactly(-1)

    def test_help(self, dummy_ctx):
        assert '3' in RequireExactly(3).help(dummy_ctx)

    def test_check_consistency(self):
        check_consistency = RequireExactly(3).check_consistency
        check_consistency(make_options('abcd'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('ab'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('abcde', required=True))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0')
        check = partial(RequireExactly(2).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'bool_opt'])  # arg1 and bool-opt
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'str_opt', 'def1'])  # arg1, str-opt, def1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'int_opt', 'flag'])  # arg1


class TestAcceptBetween:
    def test_init_raises_for_invalid_n(self):
        AcceptBetween(0, 10)
        AcceptBetween(0, 1)
        with pytest.raises(ValueError):
            AcceptBetween(-1, 2)
        with pytest.raises(ValueError):
            AcceptBetween(2, 2)
        with pytest.raises(ValueError):
            AcceptBetween(3, 2)

    def test_help(self, dummy_ctx):
        help = AcceptBetween(3, 5).help(dummy_ctx)
        assert help == 'at least 3 required, at most 5 accepted'

    def test_check_consistency(self):
        check_consistency = AcceptBetween(2, 4).check_consistency
        check_consistency(make_options('abcd'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('a'))  # too little params
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('abcde', required=True))  # too many required

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0 --flag --mul1=4')
        check = partial(AcceptBetween(2, 4).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'flag'])  # arg1, bool-opt and flag
        check(['def1', 'int_opt', 'flag', 'mul1'])  # all
        with pytest.raises(ConstraintViolated):
            check(['arg2', 'int_opt', 'def1'])  # only def1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'def1', 'def2', 'str_opt', 'flag'])  # all


class TestRequiredAll:
    def test_help(self, dummy_ctx):
        assert 'all required' in require_all.help(dummy_ctx)

    def test_check_consistency(self):
        require_all.check_consistency(make_options('abc'))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'arg1 --str-opt=0 --bool-opt=0')
        check = partial(require_all.check, ctx=ctx)
        check(['arg1'])
        check(['str_opt'])
        check(['arg1', 'str_opt'])
        check(['arg1', 'str_opt', 'bool_opt'])
        check(['arg1', 'str_opt', 'bool_opt', 'def1'])
        with pytest.raises(ConstraintViolated):
            check(['arg2'])
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'arg2'])
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'def1', 'int_opt'])


class TestRephraser:
    def test_init_raises_if_neither_help_nor_error_is_provided(self):
        with pytest.raises(ValueError):
            Rephraser(FakeConstraint())

    def test_help_override_with_string(self, dummy_ctx):
        wrapped = FakeConstraint()
        rephrased = Rephraser(wrapped, help='rephrased help')
        assert rephrased.help(dummy_ctx) == 'rephrased help'

    def test_help_override_with_function(self, dummy_ctx):
        wrapped = FakeConstraint()
        get_help = Mock(return_value='rephrased help')
        rephrased = Rephraser(wrapped, help=get_help)
        assert rephrased.help(dummy_ctx) == 'rephrased help'
        get_help.assert_called_once_with(dummy_ctx, wrapped)

    def test_error_is_overridden_passing_string(self):
        fake_ctx = make_fake_context(make_options('abcd'))
        wrapped = FakeConstraint(satisfied=False, error='__error__')
        rephrased = Rephraser(wrapped, error=f'error:\n{ErrorFmt.param_list}')
        with pytest.raises(ConstraintViolated) as exc_info:
            rephrased.check(['a', 'b'], ctx=fake_ctx)
        assert exc_info.value.message == 'error:\n  --a\n  --b\n'

    def test_error_template_key(self):
        fake_ctx = make_fake_context(make_options('abcd'))
        wrapped = FakeConstraint(satisfied=False, error='__error__')
        rephrased = Rephraser(wrapped, error=f'{ErrorFmt.error}\nExtra info here.')
        with pytest.raises(ConstraintViolated) as exc_info:
            rephrased.check(['a', 'b'], ctx=fake_ctx)
        assert str(exc_info.value) == '__error__\nExtra info here.'

    def test_error_is_overridden_passing_function(self):
        params = make_options('abc')
        fake_ctx = make_fake_context(params)
        wrapped = FakeConstraint(satisfied=False)
        error_rephraser_mock = Mock(return_value='rephrased error')
        rephrased = Rephraser(wrapped, error=error_rephraser_mock)
        with pytest.raises(ConstraintViolated, match='rephrased error'):
            rephrased.check(params, ctx=fake_ctx)

        # Check the function is called with a single argument of type ConstraintViolated
        error_rephraser_mock.assert_called_once()
        args = error_rephraser_mock.call_args[0]
        assert len(args) == 1
        error = args[0]
        assert isinstance(error, ConstraintViolated)
        # Check the error has all fields set
        assert isinstance(error.ctx, Context)
        assert isinstance(error.constraint, Constraint)
        assert len(error.params) == 3

    def test_check_consistency_raises_if_wrapped_constraint_raises(self):
        constraint = FakeConstraint(consistent=True)
        rephraser = Rephraser(constraint, help='help')
        params = make_options('abc')
        rephraser.check_consistency(params)

    def test_check_consistency_doesnt_raise_if_wrapped_constraint_doesnt_raise(self):
        constraint = FakeConstraint(consistent=False)
        rephraser = Rephraser(constraint, help='help')
        params = make_options('abc')
        with pytest.raises(UnsatisfiableConstraint):
            rephraser.check_consistency(params)
