from typing import Iterable, List

from click import Parameter


class ConstraintMixin:
    """ Provides support to constraints. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._params_by_name = {param.name: param for param in self.params}

    def get_param_by_name(self, name: str):
        try:
            return self._params_by_name[name]
        except KeyError:
            raise KeyError(f"there's no CLI parameter named '{name}'")

    def get_params_by_name(self, names: Iterable[str]) -> List[Parameter]:
        return [self.get_param_by_name(name) for name in names]

    def parse_args(self, ctx, args):
        super().parse_args(ctx, args)
        # Check OptionGroup's constraints if the command has them
        if hasattr(self, 'option_groups'):
            for group in self.option_groups:
                if group.constraint:
                    group.constraint.check(group.options, ctx=ctx)
