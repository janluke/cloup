from typing import Iterable, List, NamedTuple, Optional, Sequence, TYPE_CHECKING, Tuple

from click import Context, HelpFormatter, Parameter

from ._core import Constraint
from .common import join_param_labels

if TYPE_CHECKING:
    from .._option_groups import OptionGroup


class BoundConstraintSpec(NamedTuple):
    """A NamedTuple storing a ``Constraint`` and the **names of the parameters**
    if has check."""
    constraint: Constraint
    params: Sequence[str]


def _constraint_memo(f, spec: BoundConstraintSpec) -> None:
    store = getattr(f, '__constraints', None)
    if store is None:
        store = f.__constraints = []
    store.append(spec)


def constraint(constr: Constraint, params: Iterable[str]):
    """Registers a constraint."""
    spec = BoundConstraintSpec(constr, tuple(params))

    def wrapper(f):
        _constraint_memo(f, spec)
        return f

    return wrapper


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
        constraints: Sequence[BoundConstraintSpec] = (),
        show_constraints: bool = False,
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
        self._extra_constraints = tuple(
            BoundConstraint(constr, self.get_params_by_name(param_names))
            for constr, param_names in constraints
        )

    def parse_args(self, ctx, args):
        all_constraints = self._optgroup_constraints + self._extra_constraints
        # Check parameter groups' consistency *before* parsing
        if Constraint.must_check_consistency():
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

    def get_params_by_name(self, names: Iterable[str]) -> List[Parameter]:
        return [self.get_param_by_name(name) for name in names]

    def format_constraints(self, ctx, formatter) -> None:
        records_gen = (constr.get_help_record(ctx) for constr in self._extra_constraints)
        records = [rec for rec in records_gen if rec is not None]
        if records:
            with formatter.section('Constraints'):
                formatter.write_dl(records)

    def format_help(self, ctx, formatter: HelpFormatter) -> None:
        super().format_help(ctx, formatter)  # type: ignore
        if self.show_constraints:
            self.format_constraints(ctx, formatter)
