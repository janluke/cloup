from typing import Optional

import click
import pytest

import cloup
from cloup import Color, Group, HelpTheme, Style
from cloup._util import first_bool, identity, reindent
from cloup.styling import IStyle
from cloup.typing import MISSING


@pytest.fixture()
def cli() -> cloup.Group:
    @cloup.group()
    def cli():
        """A package installer."""

    @cloup.command(aliases=['i', 'add'])
    @cloup.argument('pkg')
    def install(pkg: str):
        """Install a package."""
        print('install', pkg)

    @cloup.group(aliases=['conf', 'cfg'])
    def config():
        """Manage the configuration."""
        print('config')

    @cloup.command(aliases=['clr'], cls=click.Command)
    def clear():
        """Remove all installed packages."""
        print('clear')

    cli.section('Commands', install, clear, config)
    return cli


cli_help_without_aliases = reindent("""
    Usage: cli [OPTIONS] COMMAND [ARGS]...

      A package installer.

    Options:
      --help  Show this message and exit.

    Commands:
      install  Install a package.
      clear    Remove all installed packages.
      config   Manage the configuration.
""")

cli_help_with_aliases = reindent("""
    Usage: cli [OPTIONS] COMMAND [ARGS]...

      A package installer.

    Options:
      --help  Show this message and exit.

    Commands:
      install (i, add)    Install a package.
      clear (clr)         Remove all installed packages.
      config (conf, cfg)  Manage the configuration.
""")


def test_command_aliases_are_stored_in_the_command(cli):
    assert cli.commands['install'].aliases == ['i', 'add']
    assert cli.commands['clear'].aliases == ['clr']


def test_simple_command_name_resolution(cli):
    ctx = cloup.Context(command=cli)
    assert cli.resolve_command_name(ctx, 'install') == 'install'
    assert cli.resolve_command_name(ctx, 'i') == 'install'
    assert cli.resolve_command_name(ctx, 'add') == 'install'

    assert cli.resolve_command_name(ctx, 'config') == 'config'
    assert cli.resolve_command_name(ctx, 'conf') == 'config'

    assert cli.resolve_command_name(ctx, 'clear') == 'clear'
    assert cli.resolve_command_name(ctx, 'clr') == 'clear'


def test_command_name_resolution_with_token_normalization_function(cli):
    ctx = cloup.Context(command=cli, token_normalize_func=str.lower)
    assert cli.resolve_command_name(ctx, 'INSTALL') == 'install'
    assert cli.resolve_command_name(ctx, 'ADD') == 'install'
    assert cli.resolve_command_name(ctx, 'CLR') == 'clear'
    assert cli.resolve_command_name(ctx, 'cONF') == 'config'


@pytest.mark.parametrize('alias', ['install', 'i', 'add'])
def test_command_resolution_with_cloup_subcommand(cli, runner, alias):
    res = runner.invoke(cli, [alias, 'cloup'])
    assert res.output.strip() == 'install cloup'


@pytest.mark.parametrize('alias', ['clear', 'clr'])
def test_command_resolution_with_click_subcommand(cli, runner, alias):
    res = runner.invoke(cli, [alias])
    assert res.output.strip() == 'clear'


@pytest.mark.parametrize(
    'cmd_value', [MISSING, None, True, False],
    ids=lambda val: f'cmd_{val}'
)
@pytest.mark.parametrize(
    'ctx_value', [MISSING, None, True, False],
    ids=lambda val: f'ctx_{val}'
)
def test_show_subcommand_aliases_setting(cli, runner, ctx_value, cmd_value):
    if ctx_value is not MISSING:
        cli.context_settings['show_subcommand_aliases'] = ctx_value
    if cmd_value is not MISSING:
        cli.show_subcommand_aliases = cmd_value

    should_show_aliases = first_bool(cmd_value, ctx_value, Group.SHOW_SUBCOMMAND_ALIASES)
    expected_help = (cli_help_with_aliases
                     if should_show_aliases
                     else cli_help_without_aliases)

    res = runner.invoke(cli, ['--help'])
    assert res.output == expected_help


def test_cloup_subcommand_help(cli, runner):
    res = runner.invoke(cli, ['i', '--help'])
    # 1. Shows the full subcommand name even if an alias was used.
    # 2. Shows aliases after help text.
    expected = reindent("""
        Usage: cli install [OPTIONS] PKG
        Aliases: i, add

          Install a package.

        Options:
          --help  Show this message and exit.
    """)
    assert res.output == expected


def test_click_subcommand_help(cli, runner):
    res = runner.invoke(cli, ['clr', '--help'])
    # Shows the full subcommand name even if an alias was used.
    # Aliases are not shown (need Cloup commands for that).
    expected = reindent("""
        Usage: cli clear [OPTIONS]

          Remove all installed packages.

        Options:
          --help  Show this message and exit.
    """)
    assert res.output == expected


def test_cloup_subgroup_help(cli, runner):
    res = runner.invoke(cli, ['conf', '--help'])
    # 1. Shows the full subcommand name even if an alias was used.
    # 2. Shows aliases after help text.
    expected = reindent("""
        Usage: cli config [OPTIONS] COMMAND [ARGS]...
        Aliases: conf, cfg

          Manage the configuration.

        Options:
          --help  Show this message and exit.
    """)
    assert res.output == expected


def test_alias_are_correctly_styled(runner):
    red = Style(fg=Color.red)
    green = Style(fg=Color.green)

    def fmt(alias: IStyle = identity, alias_secondary: Optional[IStyle] = None):
        theme = HelpTheme(alias=alias, alias_secondary=alias_secondary)
        return Group.format_subcommand_aliases(["i", "add"], theme)

    # No styles (default theme)
    assert fmt() == "(i, add)"

    # Only theme.alias
    assert fmt(alias=green) == f"{green('(i, add)')}"

    # Only theme.alias_secondary
    assert fmt(alias_secondary=green) == (
        green("(") + "i" + green(", ") + "add" + green(")")
    )

    # Both
    assert fmt(alias=red, alias_secondary=green) == (
        green("(") + red("i") + green(", ") + red("add") + green(")")
    )
