import os

import click
import cloup


@cloup.group(
    'config', aliases=['conf', 'cfg'],
    invoke_without_command=True,
    no_args_is_help=True,
)
def config():
    """Manages Manim configuration files."""
    pass


@config.command(no_args_is_help=True)
@click.option(
    "-l", "--level",
    type=click.Choice(["user", "cwd"], case_sensitive=False), default="cwd",
    help="Specify if this config is for user or the working directory.",
)
@click.option("-o", "--open", "openfile", is_flag=True)
def write(level: str, openfile: bool) -> None:
    """Writes configurations."""
    pass


@config.command()
def show():
    """Shows current configuration."""
    pass


@config.command()
@click.option("-d", "--directory", default=os.getcwd())
def export(directory):
    pass
