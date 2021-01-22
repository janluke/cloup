from unittest.mock import Mock

import pytest
from pytest import mark

from cloup.constraints import Constraint, If
from cloup.constraints.conditions import Equal, IsSet, Predicate
from tests.constraints.test_constraints import mock_constraint
from tests.util import make_context, make_options, mark_parametrize


def mock_predicate(value=True, desc='') -> Mock:
    p = Mock(Predicate, return_value=value)
    p.__and__ = Predicate.__and__
    p.__or__ = Predicate.__or__
    p.description.return_value = desc
    return p


class TestIfThenElse:

    @mark.parametrize('condition_value', [True, False])
    def test_the_right_branch_is_checked(self, sample_cmd, condition_value):
        then_ = Mock(Constraint)
        else_ = Mock(Constraint)
        ctx = make_context(sample_cmd, 'arg1 --opt1=1 --opt3=3')
        params = ['arg1', 'opt3']  # dummy params, irrelevant

        condition = mock_predicate(value=condition_value)
        constraint = If(condition).then(then_).else_(else_)
        constraint.check(params, ctx=ctx)

        if condition_value:
            then_.check_params.assert_called_once()
            else_.check_params.assert_not_called()
        else:
            then_.check_params.assert_not_called()
            else_.check_params.assert_called_once()

    def test_If_gives_informative_error_when_used_as_a_constraint(self):
        for attr in ['help', 'check', 'check_consistency']:
            with pytest.raises(AttributeError, match='forgot to call then'):
                getattr(If('ciao'), attr)
        with pytest.raises(AttributeError, match='^pippo$'):
            getattr(If('ciao'), 'pippo')

    def test_help(self, sample_cmd):
        ctx = make_context(sample_cmd, 'arg1 --opt1=1 --opt3=3')
        a = mock_constraint(help='_A_')
        b = mock_constraint(help='_B_')
        constraint = If('arg1').then(a).else_(b)
        help = constraint.help(ctx)
        assert 'ARG1' in help
        assert '_A_' in help
        assert '_B_' in help

    def test_operands_check_consistency_is_called(self):
        a = Mock(Constraint)
        b = Mock(Constraint)
        constraint = If('arg1').then(a).else_(b)
        constraint.check_consistency(make_options('abc'))
        a.check_consistency.assert_called()
        b.check_consistency.assert_called()


class TestAnd:
    @mark.parametrize('b_value', [False, True])
    @mark.parametrize('a_value', [False, True])
    def test_check(self, a_value, b_value, sample_cmd):
        ctx = make_context(sample_cmd, 'blah')
        a = mock_predicate(value=a_value)
        b = mock_predicate(value=b_value)
        c = a & b
        assert c(ctx) == (a_value and b_value)

    def test_operand_merging(self):
        a, b, c, d = (mock_predicate() for _ in range(4))
        res = (a & b) & c
        assert res.predicates == (a, b, c)
        res = (a & b) & (c & d)
        assert res.predicates == (a, b, c, d)
        res = (a & b) & (c | d)
        assert len(res.predicates) == 3

    def test_description(self, dummy_ctx):
        a, b, c = (mock_predicate(desc=name) for name in 'ABC')
        assert (a & b & c).description(dummy_ctx) == 'A and B and C'


class TestOr:
    @mark.parametrize('b_value', [False, True])
    @mark.parametrize('a_value', [False, True])
    def test_check(self, a_value, b_value, sample_cmd):
        ctx = make_context(sample_cmd, 'blah')
        a = mock_predicate(value=a_value)
        b = mock_predicate(value=b_value)
        c = a | b
        assert c(ctx) == (a_value or b_value)

    def test_operands_merging(self):
        a, b, c, d = (mock_predicate() for _ in range(4))
        res = (a | b) | c
        assert res.predicates == (a, b, c)
        res = (a | b) | (c | d)
        assert res.predicates == (a, b, c, d)
        res = (a | b) | (c & d)
        assert len(res.predicates) == 3

    def test_description(self, dummy_ctx):
        a = mock_predicate(desc='A')
        b = mock_predicate(desc='B')
        c = mock_predicate(desc='C')
        assert (a | b | c).description(dummy_ctx) == 'A or B or C'


def test_description_with_mixed_operators(dummy_ctx):
    ctx = dummy_ctx
    a, b, c, d = (mock_predicate(desc=name) for name in 'ABCD')
    assert (a & b & c).desc(ctx) == 'A and B and C'
    assert (a | b | c).desc(ctx) == 'A or B or C'
    assert (a | b & c).desc(ctx) == 'A or (B and C)'
    assert (a & b | c).desc(ctx) == '(A and B) or C'
    assert ((a | b) & (c | d)).desc(ctx) == '(A or B) and (C or D)'


class TestIsSet:
    SHELL_INPUT = 'arg1 --opt3=3 --flag2 --mul1 1 --mul1 2'

    @mark_parametrize(
        # These cases are relative to [sample_cmd] with [SHELL_INPUT] as input
        # "provided" means provided by the user in the command line
        ['param', 'is_set', 'param_kind'],
        ('arg1', True, 'provided argument'),
        ('arg2', False, 'unset argument'),
        ('opt3', True, 'provided option'),
        ('opt1', False, 'unprovided option without default'),
        ('def1', True, 'unprovided option with default'),
        ('flag', False, 'unset boolean flag'),
        ('flag2', True, 'provided boolean flag'),
        ('mul1', True, 'provided multi-option'),
        ('mul2', False, 'unprovided multi-option'),
        ('tuple', False, 'unprovided option with nargs>1'),
    )
    def test_evaluation(self, sample_cmd, param, is_set, param_kind):
        ctx = make_context(sample_cmd, self.SHELL_INPUT)
        assert IsSet(param)(ctx) == is_set, param_kind
        assert ~IsSet(param)(ctx) != is_set, param_kind

    def test_descriptions(self, sample_cmd):
        ctx = make_context(sample_cmd, '')
        assert IsSet('arg1').desc(ctx) == 'ARG1 is set'
        assert IsSet('opt1').desc(ctx) == '--opt1 is set'
        assert IsSet('arg1').neg_desc(ctx) == 'ARG1 is not set'
        assert IsSet('opt1').neg_desc(ctx) == '--opt1 is not set'


class TestEqual:
    def test_condition_Equal(self, sample_cmd):
        ctx = make_context(sample_cmd, 'xxx --opt3=3 --flag --tuple 1 2')
        for name, value in ctx.params.items():
            assert Equal(name, value)(ctx)
            assert not Equal(name, 'blah')(ctx)
            assert not (~Equal(name, value))(ctx)
            assert ~Equal(name, 'blah')(ctx)

    def test_descriptions(self, sample_cmd):
        ctx = make_context(sample_cmd, '')
        p = Equal('arg1', 'value')
        assert p.desc(ctx) == 'ARG1="value"'
        assert p.neg_desc(ctx) == 'ARG1!="value"'
