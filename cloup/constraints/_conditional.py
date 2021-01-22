"""
This modules contains classes to create conditional constraints.
"""
from typing import Sequence, Union

from click import Context, Parameter

from ._core import Constraint
from .exceptions import ConstraintViolated
from .conditions import Predicate, IsSet


def as_condition(arg: Union[str, Predicate]) -> Predicate:
    if isinstance(arg, str):
        return IsSet(arg)
    elif isinstance(arg, Predicate):
        return arg
    else:
        raise TypeError('arg "condition" should be str or Condition')


class If:
    def __init__(self, condition: Union[str, Predicate]):
        self._condition = as_condition(condition)

    def then(self, constraint: Constraint) -> '_IfThen':
        return _IfThen(self._condition, then=constraint)

    def __getattr__(self, attr):
        if attr in ['help', 'check_consistency', 'check']:
            raise AttributeError(
                "you started defining a conditional constraint with If(...) "
                "but forgot to call then(...). `If` is not a constraint, so it "
                "doesn't have a %s method" % attr
            )
        raise AttributeError(attr)

    def __repr__(self) -> str:
        return 'If(%r)' % self._condition


class _IfThen(Constraint):
    def __init__(self, condition: Predicate, then: Constraint):
        self._condition = condition
        self._then = then

    @property
    def condition(self) -> Predicate:
        return self._condition

    def help(self, ctx: Context):
        return '%s if %s' % (
            self._then.help(ctx),
            self._condition.description(ctx),
        )

    def else_(self, constraint: Constraint) -> '_IfThenElse':
        return _IfThenElse(if_then=self, else_=constraint)

    def check_consistency(self, params: Sequence[Parameter]):
        self._then.check_consistency(params)

    def check_params(self, ctx: Context, params: Sequence[Parameter]) -> bool:
        if self._condition(ctx):
            try:
                self._then.check_params(ctx, params)
                return True
            except ConstraintViolated as err:
                raise ConstraintViolated(
                    "when %s, %s" % (self._condition.description(ctx), err),
                    ctx=ctx,
                )
        return False


class _IfThenElse(Constraint):
    def __init__(self, if_then: _IfThen, else_: Constraint):
        self._if_then = if_then
        self._else = else_

    def help(self, ctx: Context):
        return '%s, otherwise %s' % (
            self._if_then.help(ctx),
            self._else.help(ctx)
        )

    def check_consistency(self, params: Sequence[Parameter]):
        self._if_then.check_consistency(params)
        self._else.check_consistency(params)

    def check_params(self, ctx: Context, params: Sequence[Parameter]):
        condition_is_true = self._if_then.check_params(ctx, params)
        if not condition_is_true:
            try:
                self._else.check_params(ctx, params)
            except ConstraintViolated as err:
                desc = self._if_then.condition.negated_description(ctx)
                raise ConstraintViolated(f'when {desc}, {err}', ctx=ctx)
