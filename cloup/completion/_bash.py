from pathlib import Path

from click.shell_completion import get_completion_class

from cloup.completion._shared import Shell, render_completion_script, upsert_snippet


def install_bash(*, prog_name: str, complete_var: str) -> Path:
    # Ref: https://github.com/scop/bash-completion#faq
    # It seems bash-completion is the official completion system for bash:
    # Ref: https://www.gnu.org/software/bash/manual/html_node/A-Programmable-Completion-Example.html
    # But installing in the locations from the docs doesn't seem to have effect

    # Write completion script
    completion_path = Path.home() / f".bash_completions/{prog_name}.sh"
    completion_path.parent.mkdir(parents=True, exist_ok=True)
    script_content = render_completion_script(
        get_completion_class(Shell.bash).source_template,
        prog_name=prog_name,
        complete_var=complete_var,
    )
    completion_path.write_text(script_content)

    # Install in ~/.bashrc
    rc_path = Path.home() / ".bashrc"
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    upsert_snippet(
        path=rc_path,
        snippet=f"source {completion_path}",
        prog_name=prog_name,
        encoding="utf-8",
    )

    return completion_path
