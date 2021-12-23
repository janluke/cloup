import cloup

print("Loading commit.py")


@cloup.command()
def commit():
    """Commit a change."""
    print("Commit!")
