import abc
from contextlib import contextmanager
from typing import (
    Callable, Iterable, Optional, Sequence, TypeVar, Union, overload
)

import click
from click import Context, Parameter

from cloup._util import check_arg, class_name, make_one_line_repr, make_repr, pluralize
from .exceptions import ConstraintViolated, UnsatisfiableConstraint
from .common import (
    get_params_whose_value_is_set,
    get_required_params,
    join_param_labels,
    param_value_is_set,
)

Op = TypeVar('Op', bound='Operator')
HelpRephraser = Callable[[Context, 'Constraint'], str]
ErrorRephraser = Callable[[Context, 'Constraint', Sequence[Parameter]], str]


class Constraint(abc.ABC):
    """
    A constraint that can be checked against an arbitrary collection of CLI
    parameters with respect to a specific :class:`click.Context` (which
    contains the values assigned to the parameters in ``ctx.params``).
    """
    __check_consistency: bool = True

    @classmethod
    def must_check_consistency(cls) -> bool:
        """Returns True if consistency checks are enabled."""
        return cls.__check_consistency

    @classmethod
    def toggle_consistency_checks(cls, value: bool):
        """Enables/disables consistency checks. Enabling means that:

        - :meth:`check` will call :meth:`check_consistency`
        - :class:`~cloup.ConstraintMixin` will call `check_consistency` on
          constraints it is responsible for before parsing CLI arguments.
        """
        cls.__check_consistency = value

    @classmethod
    @contextmanager
    def consistency_checks_toggled(cls, value: bool):
        value_to_restore = Constraint.__check_consistency
        cls.__check_consistency = value
        yield
        cls.__check_consistency = value_to_restore

    @abc.abstractmethod
    def help(self, ctx: Context) -> str:
        """A description of the constraint. """

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        """
        Performs some sanity checks that detect inconsistencies between this
        constraints and the properties of the input parameters (e.g. required).

        For example, a constraint that requires the parameters to be mutually
        exclusive is not consistent with a group of parameters with multiple
        required options.

        These sanity checks are meant to catch developer's mistakes and don't
        depend on the values assigned to the parameters; therefore:

        - they can be performed before any parameter parsing
        - they can be disabled in production (see :meth:`toggle_consistency_checks`)

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
        Raises an exception if the constraint is not satisfied by the input
        parameters in the given (or current) context.

        This method calls both :meth:`check_consistency` (if enabled) and
        :meth:`check_values`.

        .. tip::
            By default :meth:`check_consistency` is called since it shouldn't
            have any performance impact. Nonetheless, you can disable it in
            production passing ``False`` to :meth:`toggle_consistency_checks`.

        :param params: an iterable of parameter names or a sequence of
                       :class:`click.Parameter`
        :param ctx: a `Context`; if not provided, :func:`click.get_current_context`
                    is used
        :raises:
            :exc:`~cloup.constraints.ConstraintViolated`
            :exc:`~cloup.constraints.UnsatisfiableConstraint`
        """
        from ._support import ConstraintMixin

        if not params:
            raise ValueError("arg 'params' can't be empty")

        ctx = click.get_current_context() if ctx is None else ctx
        if not isinstance(ctx.command, ConstraintMixin):  # this is needed for mypy
            raise TypeError('constraints work only if the command inherits from '
                            'ConstraintMixin')

        params_objects = (ctx.command.get_params_by_name(params)
                          if isinstance(params[0], str)
                          else params)
        if self.must_check_consistency():
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

    def __call__(
        self, param_names: Iterable[str], ctx: Optional[Context] = None
    ) -> None:
        return self.check(param_names, ctx=ctx)

    def __or__(self, other: 'Constraint') -> 'Or':
        return Or(self, other)

    def __and__(self, other: 'Constraint') -> 'And':
        return And(self, other)

    def __repr__(self):
        return f'{class_name(self)}()'


class Operator(Constraint, abc.ABC):
    """Base class for all n-ary operators defined on constraints. """

    #: Used as separator of all constraints' help strings
    HELP_SEP: str

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
        return make_one_line_repr(self, help=self._help)


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


class _RequireAll(Constraint):
    """Satisfied if all parameters are set."""

    def help(self, ctx: Context) -> str:
        return 'all required'

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        values = ctx.params
        unset_params = [param for param in params
                        if not param_value_is_set(param, values[param.name])]
        if any(unset_params):
            raise ConstraintViolated(
                pluralize(
                    len(unset_params),
                    one="%s is required",
                    many="the following parameters are required:\n%s\n"
                ) % join_param_labels(unset_params),
                ctx=ctx,
            )


class RequireAtLeast(Constraint):
    """Satisfied if the number of set parameters is >= n."""

    def __init__(self, n: int):
        check_arg(n >= 0)
        self._n = n

    def help(self, ctx: Context) -> str:
        return f'at least {self._n} required'

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
                f"at least {n} of the following parameters must be set:\n"
                f"{join_param_labels(params)}.",
                ctx=ctx
            )

    def __repr__(self):
        return make_repr(self, self._n)


class AcceptAtMost(Constraint):
    """Satisfied if the number of set parameters is <= n."""

    def __init__(self, n: int):
        check_arg(n >= 0)
        self._n = n

    def help(self, ctx: Context) -> str:
        return f'at most {self._n} accepted'

    def check_consistency(self, params: Sequence[Parameter]) -> None:
        num_required_opts = len(get_required_params(params))
        if num_required_opts > self._n:
            reason = f'{num_required_opts} of the parameters are required'
            raise UnsatisfiableConstraint(self, params, reason)

    def check_values(self, params: Sequence[Parameter], ctx: Context):
        n = self._n
        given_params = get_params_whose_value_is_set(params, ctx.params)
        if len(given_params) > n:
            raise ConstraintViolated(
                f"no more than {n} of the following parameters can be set:\n"
                f"{join_param_labels(params)}.\n",
                ctx=ctx,
            )

    def __repr__(self):
        return make_repr(self, self._n)


class RequireExactly(WrapperConstraint):
    """Requires an exact number of parameters to be set."""

    def __init__(self, n: int):
        check_arg(n > 0)
        self._n = n
        super().__init__(RequireAtLeast(n) & AcceptAtMost(n), n=n)

    def help(self, ctx: Context) -> str:
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


class AcceptBetween(WrapperConstraint):
    def __init__(self, min: int, max: int):  # noqa
        """Satisfied if the number of set parameters is between
        ``min`` and ``max`` (included).

        :param min: must be an integer >= 0
        :param max: must be an integer > min
        """
        check_arg(min >= 0, 'min must be non-negative')
        if max is not None:
            check_arg(min < max, 'must be: min < max.')
        self._min = min
        self._max = max
        super().__init__(RequireAtLeast(min) & AcceptAtMost(max), min=min, max=max)

    def help(self, ctx: Context) -> str:
        return f'at least {self._min} required, at most {self._max} accepted'


#: Satisfied if all parameters are set.
require_all = _RequireAll()

#: Satisfied if none of the parameters is set.
accept_none = AcceptAtMost(0).rephrased(
    help='all forbidden',
    error='the following parameters are all forbidden'
)

#: Satisfied if either all or none of the parameters are set.
all_or_none = (require_all | accept_none).rephrased(
    help='provide all or none',
    error='either all or none of the following parameters must be set:\n{param_list}',
)

#: Satisfied if at most one of the parameters is set.
mutually_exclusive = AcceptAtMost(1).rephrased(
    help='mutually exclusive',
    error='the following parameters are mutually exclusive:\n{param_list}'
)
