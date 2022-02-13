import os
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Callable

import click
from click.shell_completion import get_completion_class

try:
    import shellingham
except ImportError:  # pragma: nocover
    shellingham = None


class Shell(str, Enum):
    bash = "bash"
    zsh = "zsh"
    fish = "fish"
    powershell = "powershell"


SUPPORTED_SHELLS = [x.value for x in Shell.__members__.values()]
SHELL_DETECTION_ENABLED = (
    shellingham is not None
    and not os.getenv("_CLOUP_COMPLETE_TEST_DISABLE_SHELL_DETECTION")
)

_invalid_identifier_char_re = re.compile(r"[^a-zA-Z0-9_]")


def render_completion_script(
    script_template: str, prog_name: str, complete_var: str
) -> str:
    cf_name = _invalid_identifier_char_re.sub("", prog_name.replace("-", "_"))
    params = dict(
        complete_func="_{}_completion".format(cf_name),
        prog_name=prog_name,
        complete_var=complete_var,
    )
    return (script_template % params).strip()


def upsert_snippet(
    path: Path,
    snippet: str,
    prog_name: str,
    make_comment: Callable[[str], str] = lambda s: f"# {s}",
    encoding: str = "utf-8",
) -> bool:
    file_content = path.read_text(encoding=encoding)

    delim_start = make_comment(f"<{prog_name}-autocomplete-installation>")
    delim_end = make_comment(f"</{prog_name}-autocomplete-installation>")

    full_snippet = f"{delim_start}\n{snippet}\n{delim_end}\n"
    prev_install_pattern = f"{delim_start}\n.+\n{delim_end}\n"
    prev_install_matcher = re.compile(prev_install_pattern)
    match = prev_install_matcher.search(file_content)
    if match:
        if match.group() == full_snippet:
            return False
        updated_content = prev_install_matcher.sub(full_snippet, file_content)
    else:
        updated_content = file_content + "\n" + full_snippet

    path.write_text(updated_content, encoding=encoding)
    return True


def get_completion_script(shell: str, prog_name: str, complete_var: str) -> str:
    script_template = get_completion_class(shell).source_template
    if script_template is None:
        click.echo(f"Shell {shell} not supported.", err=True)
        sys.exit(1)
    return render_completion_script(
        script_template, prog_name=prog_name, complete_var=complete_var
    )
