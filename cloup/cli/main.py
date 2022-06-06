import importlib
from functools import partial
from pathlib import Path

import click

import cloup
from cloup import argument, option
from cloup.cli._lib import command_to_markdown, to_markdown_plain, table_formatter

FORMATTERS = {
    'md:plain': partial(command_to_markdown, command_formatter=to_markdown_plain),
    'md:table':  partial(command_to_markdown, command_formatter=table_formatter),
}
DEFAULT_FORMAT = 'md:table'

SETTINGS = cloup.Context.settings(
    help_option_names=['-h', '--help'],
    formatter_settings=cloup.HelpFormatter.settings(
        theme=cloup.HelpTheme.dark(),
    ),
    show_subcommand_aliases=True,
    show_default=True,
)


@cloup.group('cloup', context_settings=SETTINGS)
@cloup.version_option(cloup.__version__)
def cli():
    pass


@cli.command('document', aliases=['doc'])
@argument('CMD', help="Command name specified as <module_name>:<command_name>.")
@option(
    '-o', '--out-path',
    type=cloup.Path(dir_okay=False, writable=True, path_type=Path),
    help="Path of the output file.")
@option(
    '-f', '--formatter', type=cloup.Choice(FORMATTERS), default=DEFAULT_FORMAT)
@option(
    '--toc / --no-toc', 'include_toc', default=False,
    help="Include a table of contents.")
def document_cli(cmd: str, out_path: Path, formatter: str, include_toc: bool):
    """Save the --help of a Click application to markdown."""
    module_name, symbol = cmd.split(':')
    if not symbol:
        raise click.BadParameter(
            "bad CMD argument: you must specify the name of the command inside "
            "the file (<module_name>:<command_name>")

    module = importlib.import_module(module_name)
    cmd = getattr(module, symbol)
    format_command = FORMATTERS[formatter]
    markdown = format_command(cmd, include_toc=include_toc)
    if out_path:
        out_path.parent.mkdir(exist_ok=True, parents=True)
        out_path.write_text(markdown, encoding='utf-8')
        print('File written to', out_path)
    else:
        print(markdown)


if __name__ == '__main__':
    cli()
