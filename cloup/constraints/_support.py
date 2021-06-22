from typing import (
    Callable, Iterable, NamedTuple, Optional, Sequence, TYPE_CHECKING, Tuple, Union,
)

from click import Context, HelpFormatter, Parameter

from ._core import Constraint
from .common import join_param_labels
from .._util import C, coalesce

if TYPE_CHECKING:
    from .._option_groups import OptionGroup

ParamAdder = Callable[[C], C]


class BoundConstraintSpec(NamedTuple):
    """A NamedTuple storing a ``Constraint`` and the **names of the parameters**
    if has check."""
    constraint: Constraint
    param_names: Union[Sequence[str]]

    def resolve_params(self, cmd: 'ConstraintMixin') -> 'BoundConstraint':
        return BoundConstraint(
            self.constraint,
            cmd.get_params_by_name(self.param_names)
        )


def _constraint_memo(
    f, constr: Union[BoundConstraintSpec, BoundConstraintSpec]
) -> None:
    if not hasattr(f, '__constraints'):
        f.__constraints = []
    f.__constraints.append(constr)


def constraint(constr: Constraint, params: Iterable[str]):
    """Registers a constraint on a list of parameters specified by (destination) name
    (e.g. the default name of ``--input-file`` is ``input_file``)."""
    spec = BoundConstraintSpec(constr, tuple(params))

    def decorator(f):
        _constraint_memo(f, spec)
        return f

    return decorator


def constrained_params(constr: Constraint, *param_adders: ParamAdder) -> Callable[[C], C]:
    """
    Returns a decorator that adds the given parameters and applies a constraint
    to them. Equivalent to::

        @param_adders[0]
        ...
        @param_adders[-1]
        @constraint(constr, <param names>)

    This decorator saves you to manually (re)type the parameter names.
    It can also be used inside ``@option_group``.

    Instead of using this decorator, you can also call the constraint itself::

        @constr(*param_adders)

    but remember that:

    - Python 3.9 is the first that allow arbitrary expressions in decorators,
      meaning that you can't put a parametric/conditional constraint aside ``@``
      in previous Python versions; in that case, you are better off using
      ``@constraint_params``
    - using a long conditional/composite constraint as decorator may be less
      readable.

    .. versionadded:: 0.9.0

    :param constr: an instance of :class:`Constraint`
    :param param_adders:
        function decorators, each attaching a single parameter to the decorated
        function.
    """
    def decorator(f):
        reversed_params = []
        for add_param in reversed(param_adders):
            add_param(f)
            param = f.__click_params__[-1]
            reversed_params.append(param)
        bound_constr = BoundConstraint(constr, tuple(reversed_params[::-1]))
        _constraint_memo(f, bound_constr)
        return f

    return decorator


class BoundConstraint(NamedTuple):
    """Internal utility ``NamedTuple`` that represents a ``Constraint``
    bound to a collection of ``Parameter`` instances.
    Note: this is not a subclass of Constraint."""

    constraint: Constraint
    params: Sequence[Parameter]

    def check_consistency(self):
        self.constraint.check_consistency(self.params)

    def check_values(self, ctx: Context):
        self.constraint.check_values(self.params, ctx)

    def get_help_record(self, ctx: Context) -> Optional[Tuple[str, str]]:
        constr_help = self.constraint.help(ctx)
        if not constr_help:
            return None
        param_list = '{%s}' % join_param_labels(self.params)
        return param_list, constr_help


class ConstraintMixin:
    """Provides support to constraints."""

    def __init__(
        self, *args,
        constraints: Sequence[Union[BoundConstraintSpec, BoundConstraint]] = (),
        show_constraints: Optional[bool] = None,
        **kwargs
    ):
        """
        :param args: arguments forwarded to the next class in the MRO
        :param constraints: sequence of ``BoundConstraintSpec``
        :param show_constraints:
            whether to include a "Constraint" section in the command help
        :param kwargs: keyword arguments forwarded to the next class in the MRO
        """
        super().__init__(*args, **kwargs)  # type: ignore
        self.show_constraints = show_constraints

        # This allows constraints to efficiently access parameters by name
        self._params_by_name = {param.name: param for param in self.params}  # type:ignore

        # Collect constraints applied to option groups and bind them to the
        # corresponding Option instances
        option_groups: Sequence[OptionGroup] = getattr(self, 'option_groups', [])
        self._optgroup_constraints = tuple(
            BoundConstraint(grp.constraint, grp.options)
            for grp in option_groups
            if grp.constraint is not None
        )
        # Bind constraints defined via @constraint to Parameter instances
        self._extra_constraints: Sequence[BoundConstraint] = tuple(
            (
                constr if isinstance(constr, BoundConstraint)
                else constr.resolve_params(self)
            )
            for constr in constraints
        )

    def parse_args(self, ctx, args):
        all_constraints = self._optgroup_constraints + self._extra_constraints
        # Check parameter groups' consistency *before* parsing
        if Constraint.must_check_consistency(ctx):
            for constr in all_constraints:
                constr.check_consistency()
        super().parse_args(ctx, args)
        # Validate constraints against parameter values
        for constr in all_constraints:
            constr.check_values(ctx)

    def get_param_by_name(self, name: str) -> Parameter:
        try:
            return self._params_by_name[name]
        except KeyError:
            raise KeyError(f"there's no CLI parameter named '{name}'")

    def get_params_by_name(self, names: Iterable[str]) -> Sequence[Parameter]:
        return tuple(self.get_param_by_name(name) for name in names)

    def format_constraints(self, ctx, formatter) -> None:
        records_gen = (constr.get_help_record(ctx) for constr in self._extra_constraints)
        records = [rec for rec in records_gen if rec is not None]
        if records:
            with formatter.section('Constraints'):
                formatter.write_dl(records)

    def format_help(self, ctx, formatter: HelpFormatter) -> None:
        super().format_help(ctx, formatter)  # type: ignore
        # By default, don't show constraints
        must_show_constraints = bool(coalesce(
            self.show_constraints,
            getattr(ctx, "show_constraints", None),
        ))
        if must_show_constraints:
            self.format_constraints(ctx, formatter)


def ensure_constraints_support(command) -> ConstraintMixin:
    if isinstance(command, ConstraintMixin):
        return command
    raise TypeError(
        'a Command must inherits from ConstraintMixin to support constraints')
