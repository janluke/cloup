import click

import cloup
from cloup import HelpFormatter
from cloup.styling import HelpTheme
from examples.manim.config import cfg
from examples.manim.render import render

VERSION = '0.5.0'
CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    align_option_groups=False,
    formatter_settings=HelpFormatter.settings(
        row_sep='\n',
        theme=HelpTheme.dark(),
    ),
    # color=False,
)


@cloup.group(
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
    main()
