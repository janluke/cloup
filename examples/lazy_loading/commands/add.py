import cloup

print("Loading add.py")


@cloup.command()
def add():
    """Stage a change."""
    print("Add!")
