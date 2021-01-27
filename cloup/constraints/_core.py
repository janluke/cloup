import abc
from typing import (
    Callable, Iterable, NamedTuple, Optional, Sequence, TypeVar, Union,
    overload,
)

import click
from click import Context, Parameter

from cloup._util import check_arg, class_name, make_one_line_repr, make_repr
from ._mixin import ConstraintMixin
from .exceptions import ConstraintViolated, UnsatisfiableConstraint
from .util import (
    get_required_params, get_params_whose_value_is_set, join_param_labels, pluralize,
)

Op = TypeVar('Op', bound='Operator')
HelpRephraser = Callable[[Context, 'Constraint'], str]
ErrorRephraser = Callable[[Context, 'Constraint', Sequence[Parameter]], str]


class Constraint(abc.ABC):
    """
    A constraint that can be checked on an arbitrary collection of CLI
    parameters with respect to a specific :class:`click.Context` (which
    defines the values assigned to the parameters).

    A ``Constraint`` can be bound to a specific collection of parameters calling
    the method :meth:`bind` or equivalently :meth:`__call__`, which return an
    instance of :class:`BoundConstraint`.
    """
    # TODO: make this a Context setting
    check_consistency_enabled = True

    @abc.abstractmethod
    def help(self, ctx: Context) -> str:
        """A description of the constraint. """

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        """
        Checks that this constraint is consistent with the parameters, i.e. it
        is compatible and can be satisfied by the input parameters, independently
        from what values will be assigned to them.

        For example, a constraint that requires the parameters to be mutually
        exclusive is not consistent with a group of parameters with multiple
        options required.

        The only purpose of this method is to catch mistakes of the developer.
        This checks can be disabled in production setting
        :data:`check_consistency_enabled` to ``False``.

        :param params: list of :class:`click.Parameter` instances
        :raises: :exc:`~cloup.constraints.errors.UnsatisfiableConstraint`
            if the constraint cannot be satisfied independently from the values
            provided by the user
        """

    @abc.abstractmethod
    def check_values(self, params: Sequence[Parameter], ctx: Context):
        """
        Checks that the constraint is satisfied by the input parameters in the
        given context, which (among other things) contains the values assigned
        to the parameters in ``ctx.params``.

        You probably don't want to call this method directly.
        Use :meth:`check` instead.

        :param params: list of :class:`click.Parameter` instances
        :param ctx: :class:`click.Context`
        :raises:
            :exc:`~cloup.constraints.ConstraintViolated`
        """

    @overload
    def check(self, params: Sequence[Parameter], ctx: Optional[Context] = None) -> None:
        ...  # pragma: no cover

    @overload
    def check(self, params: Iterable[str], ctx: Optional[Context] = None) -> None:
        ...  # pragma: no cover

    def check(self, params, ctx: Optional[Context] = None) -> None:
        """
        Raises an exception if the constraint is not verified by the input
        parameters in the given (or current) context.

        :param params: an iterable of parameter names or a sequence of
                       :class:`click.Parameter`
        :param ctx: a `Context`; if not provided, :func:`click.get_current_context`
                    is used
        :raises:
            :exc:`~cloup.constraints.ConstraintViolated`
            :exc:`~cloup.constraints.UnsatisfiableConstraint`
        """
        if not params:
            raise ValueError("arg 'params' can't be empty")

        ctx = click.get_current_context() if ctx is None else ctx
        if not isinstance(ctx.command, ConstraintMixin):
            raise TypeError('constraints work only if the command inherits from '
                            'ConstraintMixin')

        params_objects = (ctx.command.get_params_by_name(params)
                          if isinstance(params[0], str)
                          else params)
        if self.check_consistency_enabled:
            self.check_consistency(params_objects)
        return self.check_values(params_objects, ctx)

    def rephrased(
        self,
        help: Union[None, str, HelpRephraser] = None,
        error: Union[None, str, ErrorRephraser] = None,
    ) -> 'Rephraser':
        return Rephraser(self, help=help, error=error)

    def hidden(self) -> 'Rephraser':
        """Hides this constraint from the command help."""
        return Rephraser(self, help='')

    def bind(self, *param_names: str) -> 'BoundConstraint':
        """Returns a :class:`BoundConstraint` binding this constraint to the
        provided parameters. If you see the constraint as a curried function
        ``c(params)(ctx)``, this is equivalent to calling ``c(params)``. """
        return BoundConstraint(self, param_names)

    def __call__(self, *param_names: str) -> 'BoundConstraint':
        return self.bind(*param_names)

    def __or__(self, other: 'Constraint') -> 'Or':
        return Or(self, other)

    def __and__(self, other: 'Constraint') -> 'And':
        return And(self, other)

    def __repr__(self):
        return f'{class_name(self)}()'


class BoundConstraint(NamedTuple):
    """
    A constraint bound to a particular set of parameters.
    ``BoundConstraint`` isn't a subclass of ``Constraint``. It doesn't support
    operators, it can only be checked against a ``Context`` which contains
    values for the bound parameters.
    """
    constraint: Constraint
    param_names: Sequence[str]

    def check(self, ctx: Optional[Context] = None) -> None:
        self.constraint.check(self.param_names, ctx)

    def __call__(self, ctx: Optional[Context] = None) -> None:
        self.check(ctx)


class Operator(Constraint, abc.ABC):
    """Base class for all n-ary operators defined on constraints. """

    #: Used as separator of all constraints' help strings
    HELP_SEP = ''

    def __init__(self, *constraints: Constraint):
        """N-ary operator for constraints.
        :param constraints: operands
        """
        self.constraints = constraints

    def help(self, ctx: Context) -> str:
        return self.HELP_SEP.join(
            '(%s)' % c.help(ctx) if isinstance(c, Operator) else c.help(ctx)
            for c in self.constraints
        )

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        for c in self.constraints:
            c.check_consistency(params)

    def __repr__(self):
        return make_repr(self, *self.constraints)


class And(Operator):
    """It's satisfied if all operands are satisfied."""
    HELP_SEP = ' and '

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        for c in self.constraints:
            c.check_values(params, ctx)

    def __and__(self, other) -> 'And':
        if isinstance(other, And):
            return And(*self.constraints, *other.constraints)
        return And(*self.constraints, other)


class Or(Operator):
    """It's satisfied if at least one of the operands is satisfied."""
    HELP_SEP = ' or '

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        for c in self.constraints:
            try:
                return c.check_values(params, ctx)
            except ConstraintViolated:
                pass
        raise ConstraintViolated.default(params, self.help(ctx), ctx=ctx)

    def __or__(self, other) -> 'Or':
        if isinstance(other, Or):
            return Or(*self.constraints, *other.constraints)
        return Or(*self.constraints, other)


class Rephraser(Constraint):
    """A Constraint decorator that can override the help and/or the error
    message of the wrapped constraint.

    This is useful also for defining new constraints.
    See also :class:`WrapperConstraint`.
    """

    def __init__(
        self, constraint: Constraint,
        help: Union[None, str, HelpRephraser] = None,
        error: Union[None, str, ErrorRephraser] = None,
    ):
        if help is None and error is None:
            raise ValueError('at least one between [help] and [error] must not be None')
        self._constraint = constraint
        self._help = help
        self._error = error

    def help(self, ctx: Context) -> str:
        if self._help is None:
            return self._constraint.help(ctx)
        elif isinstance(self._help, str):
            return self._help
        else:
            return self._help(ctx, self._constraint)

    def _get_rephrased_error(
        self, ctx: Context, params: Sequence[Parameter]
    ) -> Optional[str]:
        if self._error is None:
            return None
        elif isinstance(self._error, str):
            return self._error.format(param_list=join_param_labels(params))
        else:
            return self._error(ctx, self._constraint, params)

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        try:
            self._constraint.check_consistency(params)
        except UnsatisfiableConstraint as exc:
            raise UnsatisfiableConstraint(
                self, params=params, reason=exc.reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        try:
            return self._constraint.check_values(params, ctx)
        except ConstraintViolated:
            rephrased_error = self._get_rephrased_error(ctx, params)
            if rephrased_error:
                raise ConstraintViolated(rephrased_error, ctx=ctx)
            raise

    def __repr__(self):
        return make_repr(self, self._constraint, help=self._help, error=self._error)

    def __str__(self):
        return make_one_line_repr(self, self._constraint, help=self._help)


class WrapperConstraint(Constraint, metaclass=abc.ABCMeta):
    """Abstract class that wraps another constraint and delegates all methods
    to it. Useful when you want to define a parametric constraint combining
    other existing constraints minimizing the boilerplate.

    This is an alternative to defining a function and using :class:`Rephraser`.
    Feel free to do that in your code, but cloup will stick to the convention
    that parametric constraints are defined as classes and written in
    camel-case."""

    def __init__(self, constraint: Constraint, **attrs):
        """
        :param constraint: the constraint to wrap
        :param attrs: these are just used to generate a ``__repr__`` method
        """
        self._constraint = constraint
        self._attrs = attrs

    def help(self, ctx: Context) -> str:
        return self._constraint.help(ctx)

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        try:
            self._constraint.check_consistency(params)
        except UnsatisfiableConstraint as exc:
            raise UnsatisfiableConstraint(self, params=params, reason=exc.reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        self._constraint.check_values(params, ctx)

    def __repr__(self):
        return make_repr(self, **self._attrs)


class _AllRequired(Constraint):
    """Requires all options to be set."""

    def help(self, ctx: Context) -> str:
        return 'all required'

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        values = ctx.params
        falsy_params = [param for param in params if not values[param.name]]
        if any(falsy_params):
            raise ConstraintViolated(
                pluralize(
                    len(falsy_params),
                    one="%s is required",
                    many="the following parameters are required:\n%s\n"
                ) % join_param_labels(falsy_params),
                ctx=ctx,
            )


class SetAtLeast(Constraint):
    """Requires a minimum number of parameters to be set."""

    def __init__(self, n: int):
        check_arg(n >= 0)
        self._n = n

    def help(self, ctx: Context) -> str:
        return 'at least %d required' % self._n

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        n = self._n
        if len(params) < n:
            reason = (
                f'the constraint requires a minimum of {n} parameters but '
                f'it is applied on a group of only {len(params)} parameters!'
            )
            raise UnsatisfiableConstraint(self, params, reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        n = self._n
        given_params = get_params_whose_value_is_set(params, ctx.params)
        if len(given_params) < n:
            raise ConstraintViolated(
                f"at least {n} of the following options must be set:\n"
                f"{join_param_labels(params)}.",
                ctx=ctx
            )

    def __repr__(self):
        return '%s(%d)' % (class_name(self), self._n)


class SetAtMost(Constraint):
    """Puts an upper bound to the number of set parameters."""

    def __init__(self, n: int):
        check_arg(n >= 0)
        self._n = n

    def help(self, ctx: Context) -> str:
        return f'set at most {self._n}'

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        num_required_opts = len(get_required_params(params))
        if num_required_opts > self._n:
            reason = f'{num_required_opts} of the options are required'
            raise UnsatisfiableConstraint(self, params, reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        n = self._n
        given_params = get_params_whose_value_is_set(params, ctx.params)
        if len(given_params) > n:
            raise ConstraintViolated(
                f"no more than {n} of the following options must be set:\n"
                f"{join_param_labels(params)}.\n",
                ctx=ctx,
            )

    def __repr__(self):
        return '%s(%d)' % (class_name(self), self._n)


class SetExactly(WrapperConstraint):
    """Requires an exact number of parameters to be set."""

    def __init__(self, n: int):
        check_arg(n >= 0)
        self._n = n
        super().__init__(SetAtLeast(n) & SetAtMost(n), n=n)

    def help(self, ctx: Context) -> str:
        if self._n == 0:
            return 'all forbidden'  # makes sense in conditional constraints
        return f'exactly {self._n} required'

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        n = self._n
        given_params = get_params_whose_value_is_set(params, ctx.params)
        if len(given_params) != n:
            reason = pluralize(
                count=n,
                zero='none of the following parameters must be set:\n%s\n',
                many="exactly {count} of the following parameters must be set:\n%s\n"
            ) % join_param_labels(params)
            raise ConstraintViolated(reason, ctx=ctx)


class SetBetween(WrapperConstraint):
    def __init__(self, min: int, max: int):  # noqa
        """Satisfied if the number of set options is between ``min`` and ``max``.

        :param min: must be an integer >= 0
        :param max: must be an integer > min
        """
        check_arg(min >= 0, 'min must be non-negative')
        if max is not None:
            check_arg(min < max, 'must be: min < max. Use SetExactly instead')
        self._min = min
        self._max = max
        super().__init__(SetAtLeast(min) & SetAtMost(max), min=min, max=max)

    def help(self, ctx: Context) -> str:
        return f'set at least {self._min}, at most {self._max}'


#: Requires all the parameters to be set.
all_required = _AllRequired()

#: Alias for ``SetExactly(0)``.
all_unset = SetExactly(0)

#: Requires the parameters to be either all set or all unset.
all_or_none = (all_required | all_unset).rephrased(
    help='set all or none',
    error='either all or none of the following options must be set: {param_list}"',
)

#: Rephrased version of ``SetAtMost(1)``.
mutually_exclusive = SetAtMost(1).rephrased(
    help='mutually exclusive',
)

#: Rephrased version of ``SetExactly(1)``.
required_mutually_exclusive = SetExactly(1).rephrased(
    help='required, mutually exclusive',
)


def check_constraint(
    constraint: Constraint,
    on: Sequence[str],
    ctx: Optional[Context] = None,
    error: Optional[str] = None,
) -> None:
    if error is not None:
        constraint = constraint.rephrased(error=error)
    return constraint.check(params=on, ctx=ctx)
