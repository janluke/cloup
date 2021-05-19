import shutil

import click
from click import argument, command


@command(no_args_is_help=True)
@argument('src', type=click.Path(exists=True))
@argument('dest', type=click.Path(file_okay=False))
def f(src: str, dest: str):
    """Copy a SRC file/folder to DEST with merging."""
    shutil.copytree(src, dest, dirs_exist_ok=True)


if __name__ == '__main__':
    f()
