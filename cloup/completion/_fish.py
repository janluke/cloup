from pathlib import Path

from click.shell_completion import FishComplete

from cloup.completion._shared import render_completion_script


def install_fish(*, prog_name: str, complete_var: str) -> Path:
    path_obj = Path.home() / f".config/fish/completions/{prog_name}.fish"
    parent_dir: Path = path_obj.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    script_content = render_completion_script(
        FishComplete.source_template,
        prog_name=prog_name,
        complete_var=complete_var,
    )
    path_obj.write_text(f"{script_content}\n")
    return path_obj
