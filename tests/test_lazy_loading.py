import os
import sys

from cloup._util import reindent

sys.path.append(os.path.normpath(os.path.join(__file__, "../../examples")))

from lazy_loading.cli import cli


def test_main_help(runner):
    res = runner.invoke(cli, "--help")
    assert res.output == reindent("""
        Usage: cli [OPTIONS] COMMAND [ARGS]...

        Options:
          --help  Show this message and exit.

        Commands:
          add     Add files to the staging area.
          commit  Commit changes to the repository.
          push    Push changes to a remote repository.
          stash   Stash the changes in a dirty working directory away.
    """)


def test_running_lazy_subcommand(runner):
    res = runner.invoke(cli, "add")
    assert res.output == "Add!\n"


def test_help_of_lazy_subgroup(runner):
    res = runner.invoke(cli, "stash")
    assert res.output == reindent("""
        Usage: cli stash [OPTIONS] COMMAND [ARGS]...

          Stash the changes in a dirty working directory away.

        Options:
          --help  Show this message and exit.

        Commands:
          apply  Apply stashed changes.
          pop    Apply latest stashed changes and remove them from list.
    """)


def test_running_2nd_level_lazy_subcommand(runner):
    res = runner.invoke(cli, ["stash", "pop"])
    assert res.output == "Stash pop!\n"
