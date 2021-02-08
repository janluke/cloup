"""
This modules contains classes to create conditional constraints.
"""
from typing import Optional, Sequence, Union

from click import Context, Parameter

from ._core import Constraint
from .conditions import IsSet, Predicate
from .exceptions import ConstraintViolated
from .._util import make_repr


def as_predicate(arg: Union[str, Predicate]) -> Predicate:
    if isinstance(arg, str):
        return IsSet(arg)
    elif isinstance(arg, Predicate):
        return arg
    else:
        raise TypeError('arg should be str or Predicate')


class If(Constraint):
    def __init__(
        self, condition: Union[str, Predicate],
        then: Constraint,
        else_: Optional[Constraint] = None
    ):
        self._condition = as_predicate(condition)
        self._then = then
        self._else = else_

    def help(self, ctx: Context) -> str:
        condition = self._condition.description(ctx)
        then_help = self._then.help(ctx)
        else_help = self._else.help(ctx) if self._else else None
        if not self._else:
            return f'{then_help} if {condition}'
        else:
            return f'{then_help} if {condition}, otherwise {else_help}'

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        self._then.check_consistency(params)
        if self._else:
            self._else.check_consistency(params)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        condition = self._condition
        condition_is_true = condition(ctx)
        branch = self._then if condition_is_true else self._else
        if branch is None:
            return
        try:
            branch.check_values(params, ctx=ctx)
        except ConstraintViolated as err:
            desc = (condition.description(ctx) if condition_is_true
                    else condition.negated_description(ctx))
            raise ConstraintViolated(f"when {desc}, {err}", ctx=ctx)

    def __repr__(self) -> str:
        if self._else:
            return make_repr(self, self._condition, then=self._then, else_=self._else)
        return make_repr(self, self._condition, then=self._then)
