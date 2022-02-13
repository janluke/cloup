import os
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

import click

import cloup
from ._bash import install_bash
from ._fish import install_fish
from ._powershell import install_powershell
from ._shared import (
    SHELL_DETECTION_ENABLED, SUPPORTED_SHELLS, Shell, get_completion_script, shellingham,
)
from ._zsh import install_zsh

INSTALL_FUNCS = {
    Shell.bash: install_bash,
    Shell.fish: install_fish,
    Shell.zsh: install_zsh,
    Shell.powershell: install_powershell,
}

shell_name_arg = click.Argument(
    ("shell_name",),
    type=cloup.Choice(SUPPORTED_SHELLS),
    required=not SHELL_DETECTION_ENABLED,
)


def install_completion_command(name="install-completion") -> cloup.Command:
    return cloup.Command(
        name=name,
        params=[shell_name_arg],
        callback=install_callback,
    )


@cloup.pass_context
def install_callback(ctx: click.Context, shell_name: Any) -> Any:
    if not shell_name or ctx.resilient_parsing:
        return shell_name  # pragma no cover
    if isinstance(shell_name, str):
        shell, path = install(shell=shell_name)
    else:
        shell, path = install()
    click.secho(f"{shell} completion installed in {path}", fg="green")
    click.echo("Completion will take effect once you restart the terminal")
    sys.exit(0)


def install(
    shell: Optional[str] = None,
    prog_name: Optional[str] = None,
    complete_var: Optional[str] = None,
) -> Tuple[str, Path]:
    prog_name = prog_name or click.get_current_context().find_root().info_name
    assert prog_name
    if complete_var is None:
        complete_var = "_{}_COMPLETE".format(prog_name.replace("-", "_").upper())
    if shell is None and SHELL_DETECTION_ENABLED:
        shell, _ = shellingham.detect_shell()

    if shell not in INSTALL_FUNCS:
        click.echo(f"Shell {shell} is not supported.")
        raise click.exceptions.Exit(1)

    perform_install = INSTALL_FUNCS[shell]
    installation_path = perform_install(prog_name=prog_name, complete_var=complete_var)
    return shell, installation_path


def show_completion_command(name="show-completion") -> cloup.Command:
    return cloup.Command(
        name=name,
        params=[shell_name_arg],
        callback=show_callback,
    )


@cloup.pass_context
def show_callback(ctx: click.Context, shell_name: Any) -> Any:
    if not shell_name or ctx.resilient_parsing:
        return shell_name  # pragma no cover
    prog_name = ctx.find_root().info_name
    assert prog_name
    complete_var = "_{}_COMPLETE".format(prog_name.replace("-", "_").upper())
    shell = ""
    test_disable_detection = os.getenv("_CLOUP_COMPLETE_TEST_DISABLE_SHELL_DETECTION")
    if isinstance(shell_name, str):
        shell = shell_name
    elif shellingham and not test_disable_detection:
        shell, _ = shellingham.detect_shell()
    script_content = get_completion_script(
        shell=shell, prog_name=prog_name, complete_var=complete_var,
    )
    click.echo(script_content)
    sys.exit(0)


def completion_command_section() -> cloup.Section:
    return cloup.Section(
        "Shell auto-completion",
        commands=[
            install_completion_command(),
            show_completion_command(),
        ]
    )
