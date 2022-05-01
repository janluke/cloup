import logging

import cloup
from cloup import Context
from cloup.lazy import LazyCommand, LazyGroup
from cloup.location import relative_locator

logger = logging.getLogger(__name__)


@cloup.group(context_settings=Context.settings(show_subcommand_aliases=True))
def cli():
    pass


location = relative_locator("lazy_loading.commands")

cli.section(
    "Commands",
    LazyCommand(
        "add", "Add files to the staging area.",
        location("add")
    ),
    LazyCommand(
        "commit", "Commit changes to the repository.",
        location("commit")
    ),
    LazyCommand(
        "push", "Push changes to a remote repository.",
        location("push")
    ),
    LazyGroup(
        "stash", "Stash the changes in a dirty working directory away.",
        location("stash.stash")
    )
)

if __name__ == '__main__':
    # Set logging level to DEBUG to see if you want to see when a command is loaded
    # and for accessing which attribute:
    # logging.basicConfig(level="DEBUG")

    cli("".split())
