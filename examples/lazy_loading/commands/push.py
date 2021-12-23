import cloup

print("Loading push.py")


@cloup.command()
def push():
    """Push a change."""
    print("Push!")
