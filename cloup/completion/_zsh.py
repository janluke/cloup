from pathlib import Path

from click.shell_completion import ZshComplete

from cloup.completion._shared import render_completion_script, upsert_snippet


def install_zsh(*, prog_name: str, complete_var: str) -> Path:
    # Write completion script under ~/.zfunc/
    path_obj = Path.home() / f".zfunc/_{prog_name}"
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    script_content = render_completion_script(
        ZshComplete.source_template,
        prog_name=prog_name,
        complete_var=complete_var,
    )
    path_obj.write_text(script_content)

    # Setup Zsh and load ~/.zfunc
    zshrc_path = Path.home() / ".zshrc"
    zshrc_path.parent.mkdir(parents=True, exist_ok=True)
    upsert_snippet(
        zshrc_path,
        snippet='\n'.join([
            "autoload -Uz compinit",
            "compinit",
            "zstyle ':completion:*' menu select",
            "fpath+=~/.zfunc",
        ]),
        prog_name=prog_name,
    )

    return path_obj
