from functools import partial
from typing import Sequence
from unittest import mock
from unittest.mock import Mock

import pytest
from click import Command, Context, Parameter
from pytest import mark

from cloup.constraints import (
    Constraint,
    Rephraser, SetAtLeast,
    SetAtMost,
    SetBetween,
    SetExactly,
    WrapperConstraint, all_required,
)
from cloup.constraints.exceptions import ConstraintViolated, UnsatisfiableConstraint
from tests.util import make_context, make_fake_context, make_options, should_raise


def mock_constraint(
    satisfied=True, consistent=True, help='help',
    check_error='violated', consistency_error='inconsistent',
    **kwargs,
) -> Mock:
    c = Mock(Constraint, **kwargs)
    c.__and__ = Constraint.__and__
    c.__or__ = Constraint.__or__
    c.help.return_value = help
    if not satisfied:
        c.check_values.side_effect = ConstraintViolated(check_error)
    if not consistent:
        c.check_consistency.side_effect = UnsatisfiableConstraint(
            c, [], consistency_error)
    return c


class FakeConstraint(Constraint):
    HELP = '__help__'
    ERROR = '__error__'
    CONSISTENCY_ERROR = '__inconsistent__'

    def __init__(self, satisfied=True, consistent=True):
        self.satisfied = satisfied
        self.consistent = consistent

    def help(self, ctx: Context) -> str:
        return self.HELP

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        if not self.consistent:
            raise UnsatisfiableConstraint(self, params, self.CONSISTENCY_ERROR)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        if not self.satisfied:
            raise ConstraintViolated(self.ERROR)


class TestBaseConstraint:

    def test_rephrased_defaults(self):
        with mock.patch('cloup.constraints._core.Rephraser') as rephraser_cls:
            fake = FakeConstraint()
            fake.rephrased(help='ciao')
            rephraser_cls.assert_called_with(fake, help='ciao', error=None)
            fake.rephrased(error='ciao')
            rephraser_cls.assert_called_with(fake, help=None, error='ciao')

    def test_hidden(self, dummy_ctx):
        hidden = FakeConstraint().hidden()
        assert isinstance(hidden, Rephraser)
        assert hidden.help(dummy_ctx) == ''


class TestWrapperConstraint:
    class FakeWrapper(WrapperConstraint):
        wrapped = mock_constraint()

        def __init__(self, a, b):
            super().__init__(self.wrapped, a=a, b=b)

    def test_repr(self):
        wrapper = self.FakeWrapper(1, 2)
        assert repr(wrapper) == 'FakeWrapper(a=1, b=2)'


class TestAnd:
    @mark.parametrize('b_satisfied', [False, True])
    @mark.parametrize('a_satisfied', [False, True])
    def test_check(self, a_satisfied, b_satisfied, sample_cmd):
        ctx = make_context(sample_cmd, 'blah')
        a = mock_constraint(satisfied=a_satisfied)
        b = mock_constraint(satisfied=b_satisfied)
        c = a & b
        with should_raise(ConstraintViolated, when=not (a_satisfied and b_satisfied)):
            c.check(params=['arg1', 'opt1'], ctx=ctx)

    def test_operand_merging(self):
        a, b, c, d = (mock_constraint() for _ in range(4))
        res = (a & b) & c
        assert res.constraints == (a, b, c)
        res = (a & b) & (c & d)
        assert res.constraints == (a, b, c, d)
        res = (a & b) & (c | d)
        assert len(res.constraints) == 3


class TestOr:
    @mark.parametrize('b_satisfied', [False, True])
    @mark.parametrize('a_satisfied', [False, True])
    def test_check(self, a_satisfied, b_satisfied, sample_cmd):
        ctx = make_context(sample_cmd, 'blah')
        a = mock_constraint(satisfied=a_satisfied)
        b = mock_constraint(satisfied=b_satisfied)
        c = a | b
        with should_raise(ConstraintViolated, when=not (a_satisfied or b_satisfied)):
            c.check(params=['arg1', 'opt1'], ctx=ctx)

    def test_operands_merging(self):
        a, b, c, d = (mock_constraint() for _ in range(4))
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
        ctx = make_context(sample_cmd, 'a1 --opt1=1 --opt3=3')
        check = partial(SetAtLeast(2).check, ctx=ctx)
        check(['opt1', 'opt2', 'opt3'])  # opt1 and opt3
        check(['arg1', 'opt2', 'def1'])  # arg1 and def1
        check(['arg1', 'opt1', 'def1'])  # arg1, opt1 and def1
        with pytest.raises(ConstraintViolated):
            check(['opt1', 'arg2', 'flag'])  # only opt1 is set


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
        ctx = make_context(sample_cmd, 'a1 --opt1=1 --opt3=3')
        check = partial(SetAtMost(2).check, ctx=ctx)
        check(['opt1', 'opt2', 'opt3'])      # opt1 and opt3
        check(['arg1', 'opt2', 'flag'])      # arg1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'opt1', 'def1'])  # arg1, opt1, def1


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
        ctx = make_context(sample_cmd, 'a1 --opt1=1 --opt3=3')
        check = partial(SetExactly(2).check, ctx=ctx)
        check(['opt1', 'opt2', 'opt3'])  # opt1 and opt3
        check(['arg1', 'opt2', 'opt3'])  # arg1 and opt3
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'opt1', 'def1'])  # arg1, opt1, def1
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'opt2', 'flag'])  # arg1


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


class TestAllRequired:
    def test_help(self, dummy_ctx):
        assert 'all required' in all_required.help(dummy_ctx)

    def test_check_consistency(self):
        all_required.check_consistency(make_options('abc'))

    def test_check(self, sample_cmd: Command):
        ctx = make_context(sample_cmd, 'arg1 --opt1=1 --opt3=3')
        check = partial(all_required.check, ctx=ctx)
        check(['arg1'])
        check(['opt1'])
        check(['arg1', 'opt1'])
        check(['arg1', 'opt1', 'opt3'])
        check(['arg1', 'opt1', 'opt3', 'def1'])
        with pytest.raises(ConstraintViolated):
            check(['arg2'])
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'arg2'])
        with pytest.raises(ConstraintViolated):
            check(['arg1', 'def1', 'opt2'])


class TestRephraser:
    def test_init_raises_if_neither_help_nor_error_is_provided(self):
        with pytest.raises(ValueError):
            Rephraser(FakeConstraint())

    def test_help_override_with_string(self, dummy_ctx):
        wrapped = mock_constraint()
        rephrased = Rephraser(wrapped, help='rephrased help')
        assert rephrased.help(dummy_ctx) == 'rephrased help'

    def test_help_override_with_function(self, dummy_ctx):
        wrapped = mock_constraint()
        get_help = Mock(return_value='rephrased help')
        rephrased = Rephraser(wrapped, help=get_help)
        assert rephrased.help(dummy_ctx) == 'rephrased help'
        get_help.assert_called_once_with(dummy_ctx, wrapped)

    def test_error_is_overridden_passing_string(self):
        fake_ctx = make_fake_context(make_options('abcd'))
        wrapped = mock_constraint(satisfied=False)
        rephrased = Rephraser(wrapped, error='error: {param_list}')
        with pytest.raises(ConstraintViolated) as exc_info:
            rephrased.check(['a', 'b'], ctx=fake_ctx)
        assert exc_info.value.message == 'error: --a, --b'

    def test_error_is_overridden_passing_function(self):
        params = make_options('abc')
        fake_ctx = make_fake_context(params)
        wrapped = mock_constraint(satisfied=False)
        get_error = Mock(return_value='rephrased error')
        rephrased = Rephraser(wrapped, error=get_error)
        with pytest.raises(ConstraintViolated, match='rephrased error'):
            rephrased.check(params, ctx=fake_ctx)
        get_error.assert_called_once_with(fake_ctx, wrapped, params)
        wrapped.check_consistency.assert_called_once_with(params)
        wrapped.check_values.assert_called_once_with(params, fake_ctx)

    def test_check_consistency_raises_if_wrapped_constraint_raises(self):
        constraint = mock_constraint(consistent=True)
        rephraser = Rephraser(constraint, help='help')
        params = make_options('abc')
        rephraser.check_consistency(params)
        constraint.check_consistency.assert_called_once_with(params)

    def test_check_consistency_doesnt_raise_if_wrapped_constraint_doesnt_raise(self):
        constraint = mock_constraint(consistent=False)
        rephraser = Rephraser(constraint, help='help')
        params = make_options('abc')
        with pytest.raises(UnsatisfiableConstraint):
            rephraser.check_consistency(params)
        constraint.check_consistency.assert_called_once_with(params)
