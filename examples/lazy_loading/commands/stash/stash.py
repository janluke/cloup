import cloup
from cloup.lazy import LazyCommand
from cloup.location import parent_module_of, relative_locator


@cloup.group()
def stash():
    """Stash the changes in a dirty working directory away."""
    pass


# Using lazy-loading at this level is totally optional and possibly overkill.
location = relative_locator("lazy_loading.commands.stash")
stash.section(
    "Commands",
    LazyCommand(
        "apply", "Apply stashed changes.", location("stash_apply")
    ),
    LazyCommand(
        "pop", "Apply latest stashed changes and remove them from list.",
        location("stash_pop")
    ),
)
