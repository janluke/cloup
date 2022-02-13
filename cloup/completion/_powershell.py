import os
import subprocess
from pathlib import Path
from typing import List, Tuple

import click
import click.parser
import click.shell_completion
from click.shell_completion import add_completion_class

from ._shared import Shell, render_completion_script

_SOURCE_POWERSHELL = """
Import-Module PSReadLine
Set-PSReadLineKeyHandler -Chord Tab -Function MenuComplete
$scriptblock = {
    param($wordToComplete, $commandAst, $cursorPosition)
    $Env:%(complete_var)s = "complete_powershell"
    $Env:_CLOUP_COMPLETE_ARGS = $commandAst.ToString()
    $Env:_CLOUP_COMPLETE_WORD_TO_COMPLETE = $wordToComplete
    %(prog_name)s | ForEach-Object {
        $commandArray = $_ -Split ":::"
        $command = $commandArray[0]
        $helpString = $commandArray[1]
        [System.Management.Automation.CompletionResult]::new(
            $command, $command, 'ParameterValue', $helpString)
    }
    $Env:%(complete_var)s = ""
    $Env:_CLOUP_COMPLETE_ARGS = ""
    $Env:_CLOUP_COMPLETE_WORD_TO_COMPLETE = ""
}
Register-ArgumentCompleter -Native -CommandName %(prog_name)s -ScriptBlock $scriptblock
"""


@add_completion_class
class PowerShellComplete(click.shell_completion.ShellComplete):
    name = Shell.powershell.value
    source_template = _SOURCE_POWERSHELL

    def get_completion_args(self) -> Tuple[List[str], str]:
        completion_args = os.getenv("_CLOUP_COMPLETE_ARGS", "")
        incomplete = os.getenv("_CLOUP_COMPLETE_WORD_TO_COMPLETE", "")
        cwords = click.parser.split_arg_string(completion_args)
        args = cwords[1:]
        return args, incomplete

    def format_completion(self, item: click.shell_completion.CompletionItem) -> str:
        return f"{item.value}:::{item.help or ' '}"


def install_powershell(*, prog_name: str, complete_var: str, shell: str) -> Path:
    subprocess.run(
        [
            shell,
            "-Command",
            "Set-ExecutionPolicy",
            "Unrestricted",
            "-Scope",
            "CurrentUser",
        ]
    )
    result = subprocess.run(
        [shell, "-NoProfile", "-Command", "echo", "$profile"],
        check=True,
        stdout=subprocess.PIPE,
    )
    if result.returncode != 0:  # pragma: nocover
        click.echo("Couldn't get PowerShell user profile", err=True)
        raise click.exceptions.Exit(result.returncode)
    path_str = ""
    if isinstance(result.stdout, str):  # pragma: nocover
        path_str = result.stdout
    if isinstance(result.stdout, bytes):
        try:
            # PowerShell would be predominant in Windows
            path_str = result.stdout.decode("windows-1252")
        except UnicodeDecodeError:  # pragma: nocover
            try:
                path_str = result.stdout.decode("utf8")
            except UnicodeDecodeError:
                click.echo("Couldn't decode the path automatically", err=True)
                raise click.exceptions.Exit(1)
    path_obj = Path(path_str.strip())
    parent_dir: Path = path_obj.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    script_content = render_completion_script(
        _SOURCE_POWERSHELL,
        prog_name=prog_name,
        complete_var=complete_var,
    )
    with path_obj.open(mode="a") as f:
        f.write(f"{script_content}\n")
    return path_obj
