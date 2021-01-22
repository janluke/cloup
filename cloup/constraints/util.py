"""
Utility functions for implementing constraints and conditions.
"""
from typing import Any, Dict, Iterable, List

from click import Context, Option, Parameter


def param_value_is_set(param: Parameter, value: Any) -> bool:
    """Defines what it means for a parameter to be "set"."""
    if value is None:
        return False
    elif isinstance(param, Option) and param.is_bool_flag:
        return value  # boolean flags are "set" if True
    elif param.nargs != 1 or param.multiple:
        return len(value) > 0  # params with multiple values
    return True


def get_params_whose_value_is_set(
    params: Iterable[Parameter], values: Dict[str, Any]
) -> List[Parameter]:
    """Filters ``params`` returning only the parameters that have a value.
    Boolean flags are considered "set" if their value is ``True``."""
    return [p for p in params if param_value_is_set(p, values[p.name])]


def get_required_params(params: Iterable[Parameter]) -> List[Parameter]:
    return [p for p in params if p.required]


def pluralize(
    count: int, zero: str = '', one: str = '', many: str = '',
) -> str:
    if count == 0 and zero:
        return zero
    if count == 1 and one:
        return one
    return many.format(count=count)


def get_param_label(param: Parameter) -> str:
    if param.param_type_name == 'argument':
        return param.human_readable_name
    return sorted(param.opts, key=len)[-1]


def join_param_labels(params: Iterable[Parameter], sep: str = ', ') -> str:
    return sep.join(get_param_label(p) for p in params)


def param_label_by_name(ctx, name: str) -> str:
    return get_param_label(ctx.command.get_param_by_name(name))


def param_value_by_name(ctx: Context, name: str) -> Any:
    try:
        return ctx.params[name]
    except KeyError:
        raise KeyError(f'"{name}" is not the name of a CLI parameter')
