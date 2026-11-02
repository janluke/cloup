import gettext
import struct

import pytest

import cloup
from cloup.constraints import mutually_exclusive


def write_catalog(path, messages):
    """Write a minimal GNU gettext catalog without an external msgfmt dependency."""
    messages = {"": "Content-Type: text/plain; charset=UTF-8\n", **messages}
    entries = sorted((key.encode(), value.encode()) for key, value in messages.items())
    count = len(entries)
    offset = 28 + 16 * count
    tables = []
    strings = b""
    for column in (0, 1):
        for entry in entries:
            value = entry[column]
            tables.append(struct.pack("<2I", len(value), offset + len(strings)))
            strings += value + b"\0"
    header = struct.pack("<7I", 0x950412DE, 0, count, 28, 28 + 8 * count, 0, 0)
    path.parent.mkdir(parents=True)
    path.write_bytes(header + b"".join(tables) + strings)


@pytest.fixture
def translated_labels(tmp_path, monkeypatch):
    messages = {
        "Usage:": "Uso:",
        "Aliases": "Alias",
        "Positional arguments": "Argomenti posizionali",
        "Options": "Opzioni",
        "Other options": "Altre opzioni",
        "Commands": "Comandi",
        "Other commands": "Altri comandi",
        "Constraints": "Vincoli",
        "deprecated": "obsoleto",
        "Show this message and exit.": "Mostra questo messaggio ed esci.",
        "Custom usage:": "Uso personalizzato:",
    }
    domain = "cloup-test-labels"
    write_catalog(tmp_path / "it/LC_MESSAGES" / f"{domain}.mo", messages)
    write_catalog(
        tmp_path / "fr/LC_MESSAGES" / f"{domain}.mo",
        {"Usage:": "Utilisation:", "Options": "Paramètres"},
    )
    previous_domain = gettext.textdomain()
    previous_localedir = gettext.bindtextdomain(domain)
    gettext.bindtextdomain(domain, str(tmp_path))
    gettext.textdomain(domain)
    monkeypatch.setenv("LANGUAGE", "it")
    try:
        yield messages
    finally:
        gettext.textdomain(previous_domain)
        gettext.bindtextdomain(domain, previous_localedir)


@pytest.mark.parametrize("custom_groups", [False, True])
def test_help_labels_use_application_catalog(runner, translated_labels, custom_groups):
    option_group = (
        cloup.OptionGroup("Options", help="Constraints") if custom_groups else None
    )

    @cloup.group(
        aliases=["alias"],
        deprecated="Constraints",
        help="Options",
        epilog="Commands",
        show_constraints=True,
    )
    @cloup.argument("arg", help="Aliases")
    @cloup.option("--one", is_flag=True, help="Options", group=option_group)
    @cloup.option("--two", is_flag=True)
    @cloup.constraint(mutually_exclusive, ["one", "two"])
    def cli(**kwargs):
        pass

    cli.add_command(cloup.Command("first", help="Options"))
    if custom_groups:
        cli.section("Commands", cloup.Command("second", help="Aliases"))

    result = runner.invoke(cli, ["--help"], terminal_width=80)

    assert result.exit_code == 0
    assert result.output.startswith("Uso: cli ")
    assert "Alias: alias\n" in result.output
    assert "Argomenti posizionali:\n" in result.output
    options_heading = "Altre opzioni" if custom_groups else "Opzioni"
    commands_heading = "Altri comandi" if custom_groups else "Comandi"
    assert f"{options_heading}:\n" in result.output
    assert f"{commands_heading}:\n" in result.output
    assert "Vincoli:\n" in result.output
    # Click uses the same application catalog for its built-in help option.
    assert "Mostra questo messaggio ed esci." in result.output
    # Application text is left alone even when it matches a built-in message ID.
    assert "Options (OBSOLETO: Constraints)" in result.output
    assert "ARG" in result.output and "Aliases" in result.output
    assert result.output.endswith("\nCommands\n")
    for name in ("--one", "first"):
        assert any(
            line.lstrip().startswith(name) and line.endswith("Options")
            for line in result.output.splitlines()
        )
    if custom_groups:
        assert "Options:\n" in result.output
        assert "Commands:\n" in result.output
        assert "  Constraints\n" in result.output


def test_help_labels_are_translated_when_rendered(runner, translated_labels, monkeypatch):
    @cloup.command()
    def cli():
        pass

    for language, usage, options in (
        ("it", "Uso:", "Opzioni"),
        ("fr", "Utilisation:", "Paramètres"),
        ("it", "Uso:", "Opzioni"),
        ("en", "Usage:", "Options"),
    ):
        monkeypatch.setenv("LANGUAGE", language)
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert result.output.startswith(f"{usage} cli ")
        assert f"\n{options}:\n" in result.output


@pytest.mark.parametrize(
    "prefix, expected", [(None, "Uso:"), ("Custom usage:", "Custom usage:")]
)
def test_usage_prefix_translation_preserves_theme(translated_labels, prefix, expected):
    formatter = cloup.HelpFormatter(theme=cloup.HelpTheme(heading=cloup.Style(fg="cyan")))
    formatter.write_usage("cli", prefix=prefix)
    assert formatter.getvalue() == cloup.style(expected, fg="cyan") + " cli\n"
