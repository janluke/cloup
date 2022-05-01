from typing import NamedTuple, Optional, Union


class Location(NamedTuple):
    module: str
    symbol: str

    @staticmethod
    def parse(location: str):
        parts = location.split(":")
        if len(parts) != 2:
            raise ValueError("a location should contain exactly 1 colon")
        return Location(*parts)

    def __str__(self):
        return f"{self.module}:{self.symbol}"


def as_location(location: Union[str, Location]) -> Location:
    if isinstance(location, Location):
        return location
    elif isinstance(location, str):
        return Location.parse(location)
    else:
        raise TypeError


def relative_locator(package: str):
    """Returns a function that given a relative module path and (optionally) a
    ``symbol`` name, returns a ``Location`` relative to the provided ``package``."""

    def get_relative_location(rel_path: str, symbol: Optional[str] = None) -> Location:
        symbol = symbol or rel_path.split(".")[-1]
        resolved_path = join_module_paths(package, rel_path)
        return Location(resolved_path, symbol)

    return get_relative_location


def join_module_paths(base_path: str, relative_path: str) -> str:
    base_path_parts = base_path.split(".")
    num_dots = next(
        (i for i, c in enumerate(relative_path) if c != "."),
        len(relative_path)
    )
    if num_dots == 0:
        return f"{base_path}.{relative_path}"
    elif num_dots <= len(base_path_parts):
        prefix = '.'.join(base_path_parts[:-num_dots])
        return f"{prefix}.{relative_path[num_dots:]}"
    else:
        raise ValueError(
            f"invalid relative module path: too many dots at the start: {relative_path}"
        )


def parent_module_of(module_name: str):
    parent, _, leaf = module_name.rpartition(".")
    if not leaf:
        raise ValueError(f"invalid module name: {module_name}")
    return parent
