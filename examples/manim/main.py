"""
Example based on the CLI of Manim Community, which actually uses Cloup.
This example shows how a real-world application could look like and serves to me
as a test bench for trying out styling and formatting.
"""
import cloup
from cloup import (
    Color,
    Context,
    HelpFormatter,
    HelpTheme,
    Style,
)
from cloup.formatting.sep import RowSepIf, multiline_rows_are_at_least
from config import config
from render import render

VERSION = '0.5.0'
CONTEXT_SETTINGS = Context.settings(
    help_option_names=["-h", "--help"],
    align_option_groups=False,
    align_sections=True,  # subcommand help sections
    # color=False,
    show_subcommand_aliases=True,
    formatter_settings=HelpFormatter.settings(
        # width=None,
        # max_width=80,
        # col1_max_width=30
        # col2_min_width=35,
        # indent_increment=2,
        row_sep=RowSepIf(
            multiline_rows_are_at_least(0.35),
            # sep=Hline.densely_dashed
        ),
        theme=HelpTheme.dark().with_(
            # invoked_command=Style(...),
            # command_help=Style(...),
            # heading=Style(...),
            # constraint=Style(fg='red'),
            # section_help=Style(...),
            # col1=Style(...),
            col2=Style(dim=True),
            epilog=Style(fg=Color.bright_white, italic=True),
            alias=Style(fg=Color.yellow),
            alias_secondary=Style(fg=Color.white),
        ),
    ),
)


@cloup.group(
    name='Manim',
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
    epilog="Made with <3 by Manim Community developers.",
)
@cloup.version_option(version=VERSION)
def main():
    """Animation engine for explanatory math videos."""


main.add_command(render)
main.add_command(config)

if __name__ == "__main__":
    main(prog_name='manim')
