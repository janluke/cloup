from typing import Iterable, List

from click import Parameter


class ConstraintMixin:
    """ Provides support to constraints. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._params_by_name = {param.name: param for param in self.params}
        self._optgroup_to_check = (
            [grp for grp in self.option_groups if grp.constraint]
            if hasattr(self, 'option_groups')
            else []
        )

    def get_param_by_name(self, name: str):
        try:
            return self._params_by_name[name]
        except KeyError:
            raise KeyError(f"there's no CLI parameter named '{name}'")

    def get_params_by_name(self, names: Iterable[str]) -> List[Parameter]:
        return [self.get_param_by_name(name) for name in names]

    def parse_args(self, ctx, args):
        from ._core import Constraint

        # Check group consistency *before* parameter parsing
        if Constraint.check_consistency_enabled:
            for group in self._optgroup_to_check:
                group.constraint.check_consistency(group.options)

        super().parse_args(ctx, args)

        # Check constraints against parameter values
        for group in self._optgroup_to_check:
            group.constraint.check_values(group.options, ctx)
