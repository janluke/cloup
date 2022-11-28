"""
Parameter types and "shortcuts" for creating commonly used types.
"""
import pathlib

import click


def path(
    *,
    path_type: type = pathlib.Path,
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
    allow_dash: bool = False,
) -> click.Path:
    """Shortcut for :class:`click.Path` with ``path_type=pathlib.Path``."""
    return click.Path(**locals())


def dir_path(
    *,
    path_type: type = pathlib.Path,
    exists: bool = False,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
    allow_dash: bool = False,
) -> click.Path:
    """Shortcut for :class:`click.Path` with
    ``file_okay=False, path_type=pathlib.Path``."""
    return click.Path(**locals(), file_okay=False)


def file_path(
    *,
    path_type: type = pathlib.Path,
    exists: bool = False,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
    allow_dash: bool = False,
) -> click.Path:
    """Shortcut for :class:`click.Path` with
    ``dir_okay=False, path_type=pathlib.Path``."""
    return click.Path(**locals(), dir_okay=False)
