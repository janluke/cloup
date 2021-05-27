import warnings
from typing import Any, Callable, Dict, List, Optional, Type

import click

import cloup
from cloup._util import coalesce
from cloup.formatting import HelpFormatter


def _warn_if_formatter_settings_conflict(
    ctx_key: str, formatter_key: str, ctx_kwargs: dict, formatter_settings: dict
) -> None:
    if ctx_kwargs.get(ctx_key) and formatter_settings.get(formatter_key):
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

    .. versionchanged:: 0.9.0
        Added parameter ``check_constraints_consistency``.

    .. versionadded:: 0.8.0

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
    :param show_constraints:
        whether to include a "Constraint" section in the command help (if at
        least one constraint is defined).
    :param check_constraints_consistency:
        enable additional checks for constraints which detects mistakes of the
        developer (see :meth:`cloup.Constraint.check_consistency`).
    :param formatter_settings:
        keyword arguments forwarded to :class:`HelpFormatter` in ``make_formatter``.
        This args are merged with those of the (eventual) parent context and then
        merged again (being overridden) by those of the command.
        **Tip**: use the static method :meth:`HelpFormatter.opts` to create this
        dictionary, so that you can be guided by your IDE.
    """
    formatter_class: Type[HelpFormatter] = HelpFormatter

    def __init__(
        self, *ctx_args,
        align_option_groups: Optional[bool] = None,
        align_sections: Optional[bool] = None,
        show_constraints: Optional[bool] = None,
        check_constraints_consistency: bool = True,
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
        self.show_constraints = coalesce(
            show_constraints,
            getattr(self.parent, 'show_constraints', None),
        )
        self.check_constraints_consistency = check_constraints_consistency

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

    @staticmethod
    def settings(
        *, auto_envvar_prefix: Optional[bool] = None,
        default_map: Optional[Dict[str, Any]] = None,
        terminal_width: Optional[int] = None,
        max_content_width: Optional[int] = None,
        resilient_parsing: Optional[bool] = None,
        allow_extra_args: Optional[bool] = None,
        allow_interspersed_args: Optional[bool] = None,
        ignore_unknown_options: Optional[bool] = None,
        help_option_names: Optional[List[str]] = None,
        token_normalize_func: Optional[Callable[[str], str]] = None,
        color: Optional[bool] = None,
        show_default: Optional[bool] = None,
        align_option_groups: Optional[bool] = None,
        align_sections: Optional[bool] = None,
        show_constraints: Optional[bool] = None,
        check_constraints_consistency: Optional[bool] = None,
        formatter_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Utility method for creating a ``context_settings`` dictionary.

        :param auto_envvar_prefix:
            the prefix to use for automatic environment variables. If this is
            `None` then reading from environment variables is disabled. This
            does not affect manually set environment variables which are always
            read.
        :param default_map:
            a dictionary (like object) with default values for parameters.
        :param terminal_width:
            the width of the terminal.  The default is inherit from parent
            context.  If no context defines the terminal width then auto
            detection will be applied.
        :param max_content_width:
            the maximum width for content rendered by Click (this currently
            only affects help pages).  This defaults to 80 characters if not
            overridden. In other words: even if the terminal is larger than
            that, Click will not format things wider than 80 characters by
            default.  In addition to that, formatters might add some safety
            mapping on the right.
        :param resilient_parsing:
            if this flag is enabled then Click will parse without any
            interactivity or callback invocation. Default values will also be
            ignored. This is useful for implementing things such as completion
            support.
        :param allow_extra_args:
            if this is set to `True` then extra arguments at the end will not
            raise an error and will be kept on the context. The default is to
            inherit from the command.
        :param allow_interspersed_args:
            if this is set to `False` then options and arguments cannot be
            mixed.  The default is to inherit from the command.
        :param ignore_unknown_options:
            instructs click to ignore options it does not know and keeps them
            for later processing.
        :param help_option_names:
            optionally a list of strings that define how the default help
            parameter is named. The default is ``['--help']``.
        :param token_normalize_func:
            an optional function that is used to normalize tokens (options,
            choices, etc.). This for instance can be used to implement case
            insensitive behavior.
        :param color:
            controls if the terminal supports ANSI colors or not. The default
            is autodetection. This is only needed if ANSI codes are used in
            texts that Click prints which is by default not the case. This for
            instance would affect help output.
        :param show_default: Show defaults for all options. If not set,
            defaults to the value from a parent context. Overrides an
            option's ``show_default`` argument.
        :param align_option_groups:
            if True, align the definition lists of all option groups of a command.
            You can override this by setting the corresponding argument of ``Command``
            (but you probably shouldn't: be consistent).
        :param align_sections:
            if True, align the definition lists of all subcommands of a group.
            You can override this by setting the corresponding argument of ``Group``
            (but you probably shouldn't: be consistent).
        :param show_constraints:
            whether to include a "Constraint" section in the command help (if at
            least one constraint is defined).
        :param check_constraints_consistency:
            enable additional checks for constraints which detects mistakes of the
            developer (see :meth:`cloup.Constraint.check_consistency`).
        :param formatter_settings:
            keyword arguments forwarded to :class:`HelpFormatter` in ``make_formatter``.
            This args are merged with those of the (eventual) parent context and then
            merged again (being overridden) by those of the command.
            **Tip**: use the static method :meth:`HelpFormatter.opts` to create this
            dictionary, so that you can be guided by your IDE.
        """
        return {key: val for key, val in locals().items() if val is not None}
