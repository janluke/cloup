from functools import partial
from typing import Sequence
from unittest import mock
from unittest.mock import Mock

import pytest
from click import Command, Context, Parameter
from pytest import mark

from cloup.constraints import (
    Constraint,
    Rephraser,
    SetAtLeast,
    SetAtMost,
    SetBetween,
    SetExactly,
    all_required,
)
from cloup.constraints.exceptions import ConstraintViolated, UnsatisfiableConstraint
from tests.util import make_context, make_fake_context, make_options, should_raise


class FakeConstraint(Constraint):
    """Sometimes it's useful to use::

        Mock(wraps=FakeConstraint(...))

    to create a test double with characteristics of both a mock and a fake."""

    def __init__(self, satisfied=True, consistent=True, help='help',
                 error='error', inconsistency_reason='consistency_error'):
        self.satisfied = satisfied
        self.consistent = consistent
        self._help = help
        self.error = error
        self.inconsistency_reason = inconsistency_reason

    def help(self, ctx: Context) -> str:
        return self._help

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        if not self.consistent:
            raise UnsatisfiableConstraint(self, params, self.inconsistency_reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        if not self.satisfied:
            raise ConstraintViolated(self.error, ctx=ctx)


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
            cons(['a', 'b'], ctx)

    def test_check_consistency_is_not_called_when_disabled(self):
        ctx = make_fake_context(make_options('abc'))
        dummy_params = ['a', 'b']
        with Constraint.consistency_checks_toggled(False):
            assert not Constraint.must_check_consistency()
            constr = Mock(wraps=FakeConstraint())
            constr(dummy_params, ctx)
            assert constr.check_consistency.call_count == 0
        assert Constraint.must_check_consistency()


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
    a, b, c = SetAtLeast(3), SetAtMost(10), SetExactly(8)
    a_help, b_help, c_help = (cons.help(ctx) for cons in [a, b, c])
    assert (a | b | c).help(ctx) == f'{a_help} or {b_help} or {c_help}'
    assert (a | b & c).help(ctx) == f'{a_help} or ({b_help} and {c_help})'


class TestSetAtLeast:
    def test_init_raises_for_invalid_n(self):
        SetAtLeast(0)
        with pytest.raises(ValueError):
            SetAtLeast(-1)

    def test_help(self, dummy_ctx):
        assert '3' in SetAtLeast(3).help(dummy_ctx)

    def test_check_consistency(self):
        check_consistency = SetAtLeast(3).check_consistency
        check_consistency(make_options('abc'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('ab'))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0')
        check = partial(SetAtLeast(2).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'def1'])  # arg1 and def1
        check(['arg1', 'str_opt', 'def1'])  # arg1, str-opt and def1
        with pytest.raises(ConstraintViolated):
            check(['str_opt', 'arg2', 'flag'])  # only str-opt is set


class TestSetAtMost:
    def test_init_raises_for_invalid_n(self):
        SetAtMost(0)
        with pytest.raises(ValueError):
            SetAtMost(-1)

    def test_help(self, dummy_ctx):
        assert '3' in SetAtMost(3).help(dummy_ctx)

    def test_check_consistency(self):
        check_consistency = SetAtMost(2).check_consistency
        check_consistency(make_options('abc'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('abc', required=True))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0')
        check = partial(SetAtMost(2).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'flag'])  # arg1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'str_opt', 'def1'])  # arg1, str-opt, def1


class TestSetExactly:
    def test_init_raises_for_invalid_n(self):
        with pytest.raises(ValueError):
            SetExactly(-1)

    def test_help(self, dummy_ctx):
        assert '3' in SetExactly(3).help(dummy_ctx)

    def test_check_consistency(self):
        check_consistency = SetExactly(3).check_consistency
        check_consistency(make_options('abcd'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('ab'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('abcde', required=True))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0')
        check = partial(SetExactly(2).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'bool_opt'])  # arg1 and bool-opt
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'str_opt', 'def1'])  # arg1, str-opt, def1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'int_opt', 'flag'])  # arg1


class TestSetBetween:
    def test_init_raises_for_invalid_n(self):
        SetBetween(0, 10)
        SetBetween(0, 1)
        with pytest.raises(ValueError):
            SetBetween(-1, 2)
        with pytest.raises(ValueError):
            SetBetween(2, 2)
        with pytest.raises(ValueError):
            SetBetween(3, 2)

    def test_help(self, dummy_ctx):
        help = SetBetween(3, 5).help(dummy_ctx)
        assert help == 'set at least 3, at most 5'

    def test_check_consistency(self):
        check_consistency = SetBetween(2, 4).check_consistency
        check_consistency(make_options('abcd'))
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('a'))  # too little params
        with pytest.raises(UnsatisfiableConstraint):
            check_consistency(make_options('abcde', required=True))  # too many required

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'a1 --str-opt=ciao --bool-opt=0 --flag --mul1=4')
        check = partial(SetBetween(2, 4).check, ctx=ctx)
        check(['str_opt', 'int_opt', 'bool_opt'])  # str-opt and bool-opt
        check(['arg1', 'int_opt', 'flag'])  # arg1, bool-opt and flag
        check(['def1', 'int_opt', 'flag', 'mul1'])  # all
        with pytest.raises(ConstraintViolated):
            check(['arg2', 'int_opt', 'def1'])  # only def1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'def1', 'def2', 'str_opt', 'flag'])  # all


class TestAllRequired:
    def test_help(self, dummy_ctx):
        assert 'all required' in all_required.help(dummy_ctx)

    def test_check_consistency(self):
        all_required.check_consistency(make_options('abc'))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'arg1 --str-opt=0 --bool-opt=0')
        check = partial(all_required.check, ctx=ctx)
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
        wrapped = FakeConstraint(satisfied=False)
        rephrased = Rephraser(wrapped, error='error: {param_list}')
        with pytest.raises(ConstraintViolated) as exc_info:
            rephrased.check(['a', 'b'], ctx=fake_ctx)
        assert exc_info.value.message == 'error: --a, --b'

    def test_error_is_overridden_passing_function(self):
        params = make_options('abc')
        fake_ctx = make_fake_context(params)
        wrapped = FakeConstraint(satisfied=False)
        get_error = Mock(return_value='rephrased error')
        rephrased = Rephraser(wrapped, error=get_error)
        with pytest.raises(ConstraintViolated, match='rephrased error'):
            rephrased.check(params, ctx=fake_ctx)
        get_error.assert_called_once_with(fake_ctx, wrapped, params)

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
