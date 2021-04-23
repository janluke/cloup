from typing import Optional

import click

from cloup._util import coalesce


class Context(click.Context):
    """A custom context for Cloup.

    Look up :class:`click.Context` for the list of all arguments.

    .. versionadded: 0.8.0

    :param ctx_args:
        arguments forwarded to :class:`click.Context`.
    :param ctx_kwargs:
        keyword arguments forwarded to :class:`click.Context`.
    :param align_option_groups:
        if True, align the definition lists of all option groups of a command.
        You can override this by setting the corresponding argument of ``Command``
        (but you probably shouldn't: be consistent).
    :param align_sections:
        if True, align the definition lists of all subcommands of a group.
        You can override this by setting the corresponding argument of ``Group``
        (but you probably shouldn't: be consistent).
    """

    def __init__(
        self, *ctx_args,
        align_option_groups: Optional[bool] = None,
        align_sections: Optional[bool] = None,
        **ctx_kwargs,
    ):
        super().__init__(*ctx_args, **ctx_kwargs)
        self.align_option_groups = coalesce(
            align_option_groups,
            getattr(self.parent, "align_option_groups", None)
        )
        self.align_sections = coalesce(
            align_sections,
            getattr(self.parent, "align_sections", None)
        )
