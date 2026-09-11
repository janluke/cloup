import types

import click
import pytest

import cloup


@pytest.fixture(scope="module")
def click_public_names() -> set[str]:
    return {
        name
        for name, value in vars(click).items()
        if not name.startswith("_")
        and not isinstance(value, types.ModuleType)
        and name != "annotations"
    }


def test_cloup_namespace_contains_click_public_namespace(
    click_public_names: set[str],
) -> None:
    assert click_public_names <= set(dir(cloup))


def test_cloup_all_contains_click_public_namespace(
    click_public_names: set[str],
) -> None:
    assert click_public_names <= set(cloup.__all__)


def test_warnings_module_is_not_exported_by_star_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace: dict[str, object] = {}
    with pytest.warns(DeprecationWarning):
        exec("from cloup import *", namespace)

    assert "warnings" not in cloup.__all__
    assert "warnings" not in namespace

    monkeypatch.setattr(cloup.warnings, "formatter_settings_conflict", False)
    assert cloup.warnings.formatter_settings_conflict is False


def test_click_names_are_reexported_or_intentionally_overridden(
    click_public_names: set[str],
) -> None:
    overridden = {
        name
        for name in click_public_names
        if getattr(cloup, name) is not getattr(click, name)
    }

    assert overridden == {
        "Command",
        "Context",
        "Group",
        "HelpFormatter",
        "Option",
        "argument",
        "command",
        "get_current_context",
        "group",
        "option",
        "pass_context",
    }


@pytest.mark.parametrize(
    "name",
    [
        "BaseCommand",
        "MultiCommand",
        "OptionParser",
        "get_binary_stream",
        "get_text_stream",
    ],
)
def test_deprecated_click_names_are_reexported(name: str) -> None:
    assert name in cloup.__all__
    with pytest.warns(DeprecationWarning):
        cloup_value = getattr(cloup, name)
    with pytest.warns(DeprecationWarning):
        click_value = getattr(click, name)
    assert cloup_value is click_value
