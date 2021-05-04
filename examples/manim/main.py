import click

import cloup
from cloup import Context, HelpFormatter
from cloup.styling import HelpTheme, Style
from examples.manim.config import cfg
from examples.manim.render import render

VERSION = '0.5.0'
CONTEXT_SETTINGS = Context.settings(
    help_option_names=["-h", "--help"],
    align_option_groups=False,
    align_sections=True,  # subcommand sections
    # show_default=True,
    # color=False,
    formatter_settings=HelpFormatter.settings(
        theme=HelpTheme.dark().with_(
            # heading=Style(fg='bright_blue'),
            constraint=Style(fg='red')
        ),
        indent_increment=2,
        # row_sep='\n',
    ),
)


@cloup.group(
    name='Manim',
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
    epilog="Made with <3 by Manim Community developers.",
)
@click.version_option(version=VERSION)
def main():
    """Animation engine for explanatory math videos."""
    pass


main.add_command(render)
main.add_command(cfg)

if __name__ == "__main__":
    main(prog_name='manim')
