import cloup
from lazy_loading.lib import add_to_repo


@cloup.command()
def add():
    """Stage a change."""
    print("Add!")
    add_to_repo()
