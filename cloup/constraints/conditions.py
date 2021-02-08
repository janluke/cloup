"""
This modules contains described predicates that you can use as conditions of
conditional constraints (see :class:`cloup.constraints.If`).

Predicates should be treated as immutable objects, even though immutability
is not (at the moment) enforced.
"""
import abc
from typing import Any, Generic, TypeVar

from click import Context

from .common import param_label_by_name, param_value_by_name, param_value_is_set
from ._support import ConstraintMixin
from .._util import make_repr

P = TypeVar('P', bound='Predicate')


class Predicate(abc.ABC):
    """
    A ``Callable`` that takes a ``Context`` and returns a boolean, with an
    associated description. Meant to be used as condition in a conditional
    constraint (see :class:`~cloup.constraints.If`).
    """

    @abc.abstractmethod
    def description(self, ctx: Context) -> str:
        """Succint description of the predicate (alias: `desc`)."""

    def negated_description(self, ctx: Context) -> str:
        """Succint description of the negation of this predicate (alias: `neg_desc`)."""
        return 'NOT(%s)' % self.description(ctx)

    def desc(self, ctx: Context) -> str:
        """Short alias for :meth:`description`."""
        return self.description(ctx)

    def neg_desc(self, ctx: Context) -> str:
        """Short alias for :meth:`negated_description`."""
        return self.negated_description(ctx)

    def negated(self):
        return ~self

    @abc.abstractmethod
    def __call__(self, ctx: Context) -> bool:
        """Evaluate the predicate on the given context."""

    def __invert__(self) -> 'Predicate':
        return Not(self)

    def __or__(self, other: 'Predicate') -> '_Or':
        return _Or(self, other)

    def __and__(self, other: 'Predicate') -> '_And':
        return _And(self, other)

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class Not(Predicate, Generic[P]):
    def __init__(self, predicate: P):
        self._predicate = predicate

    def description(self, ctx: Context) -> str:
        return self._predicate.negated_description(ctx)

    def negated_description(self, ctx: Context) -> str:
        return self._predicate.description(ctx)

    def __call__(self, ctx: Context) -> bool:
        return not self._predicate(ctx)

    def __invert__(self) -> P:
        return self._predicate

    def __repr__(self) -> str:
        return 'Not(%r)' % self._predicate


class _Operator(Predicate, metaclass=abc.ABCMeta):
    DESC_SEP: str

    def __init__(self, *predicates):
        self.predicates = predicates

    def description(self, ctx: Context) -> str:
        return self.DESC_SEP.join(
            '(%s)' % p.description(ctx) if isinstance(p, _Operator)
            else p.description(ctx)
            for p in self.predicates
        )

    def __repr__(self):
        return make_repr(self, *self.predicates)


class _And(_Operator):
    DESC_SEP = ' and '

    def __call__(self, ctx: Context) -> bool:
        return all(c(ctx.params) for c in self.predicates)

    def __and__(self, other: 'Predicate') -> '_And':
        if isinstance(other, _And):
            return _And(*self.predicates, *other.predicates)
        return _And(*self.predicates, other)


class _Or(_Operator):
    DESC_SEP = ' or '

    def __call__(self, ctx: Context) -> bool:
        return any(c(ctx.params) for c in self.predicates)

    def __or__(self, other: 'Predicate') -> '_Or':
        if isinstance(other, _Or):
            return _Or(*self.predicates, *other.predicates)
        return _Or(*self.predicates, other)


class IsSet(Predicate):
    def __init__(self, param_name: str):
        """True if the parameter is set."""
        self.param_name = param_name

    def description(self, ctx: Context) -> str:
        return '%s is set' % param_label_by_name(ctx, self.param_name)

    def negated_description(self, ctx: Context) -> str:
        return '%s is not set' % param_label_by_name(ctx, self.param_name)

    def __call__(self, ctx: Context) -> bool:
        if not isinstance(ctx.command, ConstraintMixin):
            raise TypeError(
                'a Command must inherits from ConstraintMixin to support constraints')
        param = ctx.command.get_param_by_name(self.param_name)
        value = param_value_by_name(ctx, self.param_name)
        return param_value_is_set(param, value)


class Equal(Predicate):
    """True if the parameter value equals ``value``."""
    def __init__(self, param_name: str, value: Any):
        self.param_name = param_name
        self.value = value

    def description(self, ctx: Context) -> str:
        param_label = param_label_by_name(ctx, self.param_name)
        return f'{param_label}="{self.value}"'

    def negated_description(self, ctx: Context) -> str:
        param_label = param_label_by_name(ctx, self.param_name)
        return f'{param_label}!="{self.value}"'

    def __call__(self, ctx: Context) -> bool:
        return param_value_by_name(ctx, self.param_name) == self.value
