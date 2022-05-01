import cloup
from lazy_loading.lib import pop_stashed_changes


@cloup.command()
def stash_pop():
    print("Stash pop!")
    pop_stashed_changes()
