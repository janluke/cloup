import click


class Context(click.Context):
    """A Context that adds a ``formatter_factory`` instance argument."""

    def __init__(
        self, *args,
        align_option_groups: bool = True,
        align_sections: bool = True,
        **ctx_kwargs,
    ):
        super().__init__(*args, **ctx_kwargs)
        self.align_option_groups = align_option_groups
        self.align_sections = align_sections
