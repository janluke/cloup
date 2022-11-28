import os

import cloup


@cloup.group(
    'config', aliases=['conf', 'cfg'],
    invoke_without_command=True,
    no_args_is_help=True,
)
def config():
    """Manage Manim configuration files."""


@config.command(no_args_is_help=True)
@cloup.option(
    "-l", "--level",
    type=cloup.Choice(["user", "cwd"], case_sensitive=False), default="cwd",
    help="Specify if this config is for user or the working directory.",
)
@cloup.option("-o", "--open", "openfile", is_flag=True)
def write(level: str, openfile: bool) -> None:
    """Write configurations."""


@config.command()
def show():
    """Show current configuration."""


@config.command()
@cloup.option("-d", "--directory", default=os.getcwd())
def export(directory):
    pass
