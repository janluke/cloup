from itertools import combinations
from typing import Optional
from unittest.mock import Mock

import pytest
from click import Context
from pytest import mark

from cloup.constraints import ConstraintViolated, If
from cloup.constraints.conditions import (
    AllSet, AnySet, Equal, IsSet, Predicate, _And, _Or
)
from tests.constraints.test_constraints import FakeConstraint
from tests.util import make_context, parametrize, mock_repr


class FakePredicate(Predicate):
    def __init__(self, value: bool = True,
                 desc: str = 'description',
                 neg_desc: Optional[str] = None):
        self.value = value
        self._desc = desc
        self._neg_desc = neg_desc

    def description(self, ctx: Context) -> str:
        assert isinstance(ctx, Context)
        return self._desc

    def negated_description(self, ctx: Context) -> str:
        assert isinstance(ctx, Context)
        if self._neg_desc:
            return self._neg_desc
        return super().negated_description(ctx)

    def __call__(self, ctx: Context) -> bool:
        assert isinstance(ctx, Context)
        return self.value


class TestIf:

    def test_help(self, sample_cmd):
        ctx = make_context(sample_cmd, 'arg1 --str-opt=ciao --bool-opt=0')
        condition = FakePredicate(desc='<condition>')
        then_branch = FakeConstraint(help='<a>')
        else_branch = FakeConstraint(help='<b>')

        constr = If(condition, then_branch)
        assert constr.help(ctx) == '<a> if <condition>'

        constr = If(condition, then_branch, else_branch)
        assert constr.help(ctx) == '<a> if <condition>, otherwise <b>'

    @mark.parametrize('condition_is_true', [True, False])
    @mark.parametrize(
        'else_is_provided', [True, False], ids=['else_given', 'else_missing']
    )
    def test_branches_check_methods_are_called_correctly(
        self, sample_cmd, condition_is_true, else_is_provided
    ):
        ctx = make_context(sample_cmd, 'arg1 --str-opt=ciao --bool-opt=0')
        param_names = ['arg1', 'bool_opt']
        params = sample_cmd.get_params_by_name(param_names)

        then_branch = Mock(wraps=FakeConstraint())
        else_branch = Mock(wraps=FakeConstraint()) if else_is_provided else None
        constraint = If(
            condition=FakePredicate(value=condition_is_true),
            then=then_branch,
            else_=else_branch
        )
        constraint.check(param_names, ctx=ctx)

        # check_consistency() is called on both branches whatever the condition value is
        then_branch.check_consistency.assert_called_once_with(params)
        if else_is_provided:
            else_branch.check_consistency.assert_called_once_with(params)

        if condition_is_true:
            then_branch.check_values.assert_called_once_with(params, ctx=ctx)
            if else_is_provided:
                else_branch.check_values.assert_not_called()
        else:
            then_branch.check_values.assert_not_called()
            if else_is_provided:
                else_branch.check_values.assert_called_once_with(params, ctx=ctx)

    def test_error_message(self, sample_cmd):
        ctx = make_context(sample_cmd, 'arg1 --str-opt=ciao --bool-opt=0')
        dummy_params = ['arg1', 'bool_opt']
        then_branch = FakeConstraint(satisfied=False, error='<then_error>')
        else_branch = FakeConstraint(satisfied=False, error='<else_error>')

        true_predicate = FakePredicate(True, desc='<true>')
        with pytest.raises(ConstraintViolated) as info:
            If(true_predicate, then_branch, else_branch).check(dummy_params, ctx=ctx)
        assert info.value.message == 'when <true>, <then_error>'

        false_predicate = FakePredicate(False, desc='<true>', neg_desc='<false>')
        with pytest.raises(ConstraintViolated) as info:
            If(false_predicate, then_branch, else_branch).check(dummy_params, ctx=ctx)
        assert info.value.message == 'when <false>, <else_error>'

    def test_init_with_string_as_condition(self):
        constr = If('name', FakeConstraint())
        assert isinstance(constr._condition, IsSet)
        assert constr._condition.param_name == 'name'

    def test_init_with_sequence_of_strings_as_condition(self):
        param_names = ('opt1', 'opt2')
        constr = If(param_names, FakeConstraint())
        assert isinstance(constr._condition, AllSet)
        assert constr._condition.param_names == param_names

    def test_repr(self):
        predicate = mock_repr('<Predicate>', spec=FakePredicate, wraps=FakePredicate())
        then_branch = mock_repr('<ThenBranch>', wraps=FakeConstraint())
        else_branch = mock_repr('<ElseBranch>', wraps=FakeConstraint())

        constr = If(predicate, then_branch)
        assert repr(constr) == 'If(<Predicate>, then=<ThenBranch>)'
        constr = If(predicate, then_branch, else_branch)
        assert repr(constr) == 'If(<Predicate>, then=<ThenBranch>, else_=<ElseBranch>)'


class TestNot:
    def test_descriptions(self, dummy_ctx):
        neg = ~FakePredicate(desc='<desc>')
        assert neg.desc(dummy_ctx) == 'NOT(<desc>)'
        assert neg.neg_desc(dummy_ctx) == '<desc>'

        neg = ~FakePredicate(desc='<desc>', neg_desc='<neg_desc>')
        assert neg.desc(dummy_ctx) == '<neg_desc>'
        assert neg.neg_desc(dummy_ctx) == '<desc>'

    def test_double_negation_returns_original_predicate(self):
        fake = FakePredicate()
        assert ~~fake is fake


class TestAnd:
    @mark.parametrize('b_value', [False, True])
    @mark.parametrize('a_value', [False, True])
    def test_evaluation(self, a_value, b_value, dummy_ctx):
        a = FakePredicate(value=a_value)
        b = FakePredicate(value=b_value)
        c = a & b
        assert c(dummy_ctx) == (a_value and b_value)

    def test_operand_merging(self):
        a, b, c, d = (FakePredicate() for _ in range(4))
        res = (a & b) & c
        assert res.predicates == (a, b, c)
        res = (a & b) & (c & d)
        assert res.predicates == (a, b, c, d)
        res = (a & b) & (c | d)
        assert len(res.predicates) == 3

    def test_descriptions(self, dummy_ctx):
        a, b, c = (FakePredicate(desc=name) for name in 'ABC')
        assert (a & b & c).description(dummy_ctx) == 'A and B and C'
        assert (a & b & c).neg_desc(dummy_ctx) == 'NOT(A) or NOT(B) or NOT(C)'


class TestOr:
    @mark.parametrize('b_value', [False, True])
    @mark.parametrize('a_value', [False, True])
    def test_evaluation(self, a_value, b_value, dummy_ctx):
        a = FakePredicate(value=a_value)
        b = FakePredicate(value=b_value)
        c = a | b
        assert c(dummy_ctx) == (a_value or b_value)

    def test_operands_merging(self):
        a, b, c, d = (FakePredicate() for _ in range(4))
        res = (a | b) | c
        assert res.predicates == (a, b, c)
        res = (a | b) | (c | d)
        assert res.predicates == (a, b, c, d)
        res = (a | b) | (c & d)
        assert len(res.predicates) == 3

    def test_descriptions(self, dummy_ctx):
        a, b, c = (FakePredicate(desc=desc) for desc in 'ABC')
        assert (a | b | c).description(dummy_ctx) == 'A or B or C'
        assert (a | b | c).neg_desc(dummy_ctx) == 'NOT(A) and NOT(B) and NOT(C)'


def test_description_with_mixed_operators(dummy_ctx):
    ctx = dummy_ctx
    a, b, c, d = (FakePredicate(desc=desc) for desc in 'ABCD')
    assert (a & b & c).desc(ctx) == 'A and B and C'
    assert (a | b | c).desc(ctx) == 'A or B or C'
    assert (a | b & c).desc(ctx) == 'A or (B and C)'
    assert (a & b | c).desc(ctx) == '(A and B) or C'
    assert ((a | b) & (c | d)).desc(ctx) == '(A or B) and (C or D)'


class TestIsSet:
    SHELL_INPUT = 'arg1 --bool-opt=0 --flag2 --mul1 1 --mul1 2'

    @parametrize(
        # These cases are relative to [sample_cmd] with [SHELL_INPUT] as input
        # "provided" means provided by the user in the command line
        ['param', 'is_set'],
        pytest.param('arg1',     True,  id='provided argument'),
        pytest.param('arg2',     False, id='unset argument'),
        pytest.param('bool_opt', True,  id='provided option'),
        pytest.param('str_opt',  False, id='unprovided option without default'),
        pytest.param('def1',     True,  id='unprovided option with default'),
        pytest.param('flag',     False, id='unset boolean flag'),
        pytest.param('flag2',    True,  id='provided boolean flag'),
        pytest.param('mul1',     True,  id='provided multi-option'),
        pytest.param('mul2',     False, id='unprovided multi-option'),
        pytest.param('tuple',    False, id='unprovided option with nargs>1'),
    )
    def test_evaluation(self, sample_cmd, param, is_set):
        ctx = make_context(sample_cmd, self.SHELL_INPUT)
        assert IsSet(param)(ctx) == is_set
        assert ~IsSet(param)(ctx) != is_set

    def test_descriptions(self, sample_cmd):
        ctx = make_context(sample_cmd, '')
        assert IsSet('arg1').desc(ctx) == 'ARG1 is set'
        assert IsSet('str_opt').desc(ctx) == '--str-opt is set'
        assert IsSet('arg1').neg_desc(ctx) == 'ARG1 is not set'
        assert IsSet('str_opt').neg_desc(ctx) == '--str-opt is not set'

    def test_and(self):
        a, b, c = IsSet('opt1'), IsSet('opt2'), Equal('opt2', 'value')
        assert a & b == AllSet('opt1', 'opt2')
        assert a & c == _And(a, c)

    def test_or(self):
        a, b, c = IsSet('opt1'), IsSet('opt2'), Equal('opt2', 'value')
        assert a | b == AnySet('opt1', 'opt2')
        assert a | c == _Or(a, c)

    def test_eq(self):
        assert IsSet('a') == IsSet('a')
        assert IsSet('a') != IsSet('b')
        assert IsSet('a') != Equal('a', 'ciao')


class TestEqual:
    def test_evaluation(self, sample_cmd):
        ctx = make_context(sample_cmd, 'xxx --bool-opt=0 --flag --tuple 1 2')
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

    def test_eq(self):
        assert Equal('name', 'value') == Equal('name', 'value')
        assert Equal('name', 'foo') != Equal('name', 'bar')
        assert Equal('foo', 'value') != Equal('bar', 'value')


class TestAllSet:
    def test_evaluation_of_true_predicates(self, sample_cmd):
        ctx = make_context(sample_cmd, 'xxx --bool-opt=0 --flag --tuple 1 2')
        set_params = ['arg1', 'bool_opt', 'flag', 'tuple']
        for n in range(1, len(set_params)):
            for param_group in combinations(set_params, n):
                true = AllSet(*param_group)
                assert true(ctx), param_group
                assert not (~true)(ctx), param_group

    def test_evaluation_of_false_predicates(self, sample_cmd):
        ctx = make_context(sample_cmd, 'xxx --bool-opt=0 --flag --tuple 1 2')
        param_groups = [('arg1', 'arg2'), ('arg1', 'int_opt'), ('arg2', 'str_opt')]
        for param_group in param_groups:
            false = AllSet(*param_group)
            assert not false(ctx), param_group
            assert (~false)(ctx), param_group

    def test_descriptions(self, sample_cmd):
        ctx = make_context(sample_cmd, '')
        assert AllSet('arg1').desc(ctx) == 'ARG1 is set'
        assert AllSet('arg1').neg_desc(ctx) == 'ARG1 is not set'

        assert AllSet('arg1', 'flag').desc(ctx) \
               == 'ARG1 and --flag are both set'
        assert AllSet('arg1', 'flag').neg_desc(ctx) \
               == 'ARG1 and --flag are not both set'

        assert AllSet('arg1', 'flag', 'int_opt').desc(ctx) \
               == 'ARG1, --flag and --int-opt are all set'
        assert AllSet('arg1', 'flag', 'int_opt').neg_desc(ctx) \
               == 'ARG1, --flag and --int-opt are not all set'

    def test_and(self):
        allset1 = AllSet('a', 'b')
        allset2 = AllSet('c', 'd')
        anyset = AnySet('foo', 'bar')
        assert allset1 & allset2 == AllSet('a', 'b', 'c', 'd')
        assert allset1 & anyset == _And(allset1, anyset)

    def test_eq(self):
        assert AllSet('a', 'b') == AllSet('a', 'b')
        assert AllSet('a') != AllSet('a', 'b')
        assert AllSet('a', 'b') != AnySet('a', 'b')


class TestAnySet:
    def test_evaluation(self, sample_cmd):
        ctx = make_context(sample_cmd, 'xxx --bool-opt=0 --flag --tuple 1 2')
        set_params = ['arg1', 'bool_opt', 'flag', 'tuple']
        unset_params = ['arg2', 'int_opt', 'str_opt']
        for set_param in set_params:
            true = AnySet(*unset_params, set_param)
            assert true(ctx)
            assert not (~true)(ctx)
        false = AnySet(*unset_params)
        assert not false(ctx)
        assert (~false)(ctx)

    def test_descriptions(self, sample_cmd):
        ctx = make_context(sample_cmd, '')
        assert AnySet('arg1').desc(ctx) == 'ARG1 is set'
        assert AnySet('arg1').neg_desc(ctx) == 'ARG1 is not set'

        assert AnySet('arg1', 'flag').desc(ctx) \
               == 'either ARG1 or --flag is set'
        assert AnySet('arg1', 'flag').neg_desc(ctx) \
               == 'neither ARG1 nor --flag is set'

        assert AnySet('arg1', 'flag', 'int_opt').desc(ctx) \
               == 'any of ARG1, --flag and --int-opt is set'
        assert AnySet('arg1', 'flag', 'int_opt').neg_desc(ctx) \
               == 'none of ARG1, --flag and --int-opt is set'

    def test_or(self):
        anyset1 = AnySet('a', 'b')
        anyset2 = AnySet('c', 'd')
        allset = AllSet('foo', 'bar')
        assert anyset1 | anyset2 == AnySet('a', 'b', 'c', 'd')
        assert anyset1 | allset == _Or(anyset1, allset)

    def test_eq(self):
        assert AnySet('a', 'b') == AnySet('a', 'b')
        assert AnySet('a') != AnySet('a', 'b')
        assert AnySet('a', 'b') != AllSet('a', 'b')
