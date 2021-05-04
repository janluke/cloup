import warnings
from typing import Any, Dict, Optional

import click

import cloup
from cloup._util import coalesce
from cloup.formatting import FormatterMaker, HelpFormatter


def _warn_if_formatter_settings_conflict(ctx_key, formatter_key, ctx_kwargs, formatter_settings):
    if (ctx_key in ctx_kwargs) and (formatter_key in formatter_settings):
        from textwrap import dedent
        formatter_arg = f'formatter_settings.{formatter_key}'
        warnings.warn(dedent(f"""
        You provided both {ctx_key} and {formatter_arg} as arguments of a Context.
        Unless you have a particular reason, you should set only one of them..
        If you use both, {formatter_arg} will be used by the formatter.
        You can suppress this warning by setting:

            cloup.warnings.formatter_settings_conflict = False
        """))


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
    :param formatter_settings:
        keyword arguments forwarded to :class:`HelpFormatter` in ``make_formatter``.
        This args are merged with those of the (eventual) parent context and then
        merged again (being overridden) by those of the command.
        **Tip**: use the static method :meth:`HelpFormatter.opts` to create this
        dictionary, so that you can be guided by your IDE.
    """
    formatter_class: FormatterMaker = HelpFormatter

    def __init__(
        self, *ctx_args,
        align_option_groups: Optional[bool] = None,
        align_sections: Optional[bool] = None,
        formatter_settings: Dict[str, Any] = {},
        **ctx_kwargs,
    ):
        super().__init__(*ctx_args, **ctx_kwargs)
        self.align_option_groups = coalesce(
            align_option_groups,
            getattr(self.parent, 'align_option_groups', None),
        )
        self.align_sections = coalesce(
            align_sections,
            getattr(self.parent, 'align_sections', None),
        )

        if cloup.warnings.formatter_settings_conflict:
            _warn_if_formatter_settings_conflict(
                'terminal_width', 'width', ctx_kwargs, formatter_settings)
            _warn_if_formatter_settings_conflict(
                'max_content_width', 'max_width', ctx_kwargs, formatter_settings)

        #: Keyword arguments for the HelpFormatter. Obtained by merging the options
        #: of the parent context with the one passed to this context. Before creating
        #: the help formatter, these options are merged with the (eventual) options
        #: provided to the command (having higher priority).
        self.formatter_settings = {
            **getattr(self.parent, 'formatter_settings', {}),
            **formatter_settings,
        }

    def get_formatter_settings(self) -> Dict[str, Any]:
        return {
            'width': self.terminal_width,
            'max_width': self.max_content_width,
            **self.formatter_settings,
            **getattr(self.command, 'formatter_settings', {})
        }

    def make_formatter(self) -> HelpFormatter:
        opts = self.get_formatter_settings()
        return self.formatter_class(**opts)
