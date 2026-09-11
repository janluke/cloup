import inspect
from collections.abc import Callable
from dataclasses import dataclass

import click
import pytest
from typing_extensions import assert_type

from cloup._util import identity
from cloup.styling import Color, HelpTheme, IStyle, Style


@dataclass(frozen=True)
class CustomTheme(HelpTheme):
    metavar: IStyle = identity
    label: str | None = "default"


@dataclass(frozen=True)
class PresetTheme(CustomTheme):
    @classmethod
    def dark(cls) -> "PresetTheme":
        return super().dark().with_(metavar=Style(fg="cyan"))

    @classmethod
    def light(cls) -> "PresetTheme":
        return super().light().with_(metavar=Style(fg="blue"))


def test_help_theme_copy_with():
    s1, s2 = Style(), Style()
    r1, r2 = Style(), Style()
    theme = HelpTheme(heading=s1, col1=s2).with_(col1=r1, col2=r2)
    assert theme == HelpTheme(heading=s1, col1=r1, col2=r2)


def test_help_theme_copy_with_takes_the_same_parameters_of_constructor():
    def get_param_names(func):
        params = inspect.signature(func).parameters
        return [name for name, param in params.items() if param.kind != param.VAR_KEYWORD]

    constructor_params = get_param_names(HelpTheme)
    method_params = get_param_names(HelpTheme.with_)[1:]  # skip self
    assert method_params == constructor_params


def test_help_theme_default_themes():
    assert isinstance(HelpTheme.dark(), HelpTheme)
    assert isinstance(HelpTheme.light(), HelpTheme)


@pytest.mark.parametrize("preset", ["dark", "light"])
def test_help_theme_subclass_default_themes(preset: str) -> None:
    theme = getattr(CustomTheme, preset)()
    base_theme = getattr(HelpTheme, preset)()
    assert type(theme) is CustomTheme
    assert theme.metavar is identity
    assert theme.label == "default"
    for name in inspect.signature(HelpTheme).parameters:
        assert getattr(theme, name) == getattr(base_theme, name)


@pytest.mark.parametrize("factory", [CustomTheme, CustomTheme.dark, CustomTheme.light])
def test_help_theme_subclass_copy_with(factory: Callable[[], CustomTheme]) -> None:
    original = factory()
    metavar, heading = Style(fg="cyan"), Style(bold=True)
    theme = original.with_(metavar=metavar, heading=heading, label=None)

    assert_type(theme, CustomTheme)
    assert type(theme) is CustomTheme
    assert theme.metavar is metavar
    assert theme.heading is heading
    assert theme.label is None
    assert theme.col1 == original.col1
    assert original.metavar is identity
    assert original.label == "default"

    updated = theme.with_(col2=Style(fg="red"))
    assert type(updated) is CustomTheme
    assert updated.metavar is metavar
    assert updated.label is None
    assert theme.with_() is theme
    assert theme.with_(heading=None) is theme


@pytest.mark.parametrize("factory", [HelpTheme, CustomTheme])
def test_help_theme_copy_with_alias_secondary(factory: Callable[[], HelpTheme]) -> None:
    style = Style(fg="cyan")
    theme = factory().with_(alias_secondary=style)
    assert theme.alias_secondary is style
    assert theme.with_().alias_secondary is style
    assert theme.with_(heading=style).alias_secondary is style
    assert theme.with_(alias_secondary=None).alias_secondary is style


@pytest.mark.parametrize("factory", [HelpTheme, CustomTheme])
def test_help_theme_copy_with_rejects_unknown_fields(factory: Callable[[], HelpTheme]):
    with pytest.raises(TypeError, match="unexpected keyword argument 'unknown'"):
        factory().with_(unknown=Style())


def test_help_theme_return_types() -> None:
    assert_type(HelpTheme.dark(), HelpTheme)
    assert_type(HelpTheme.light(), HelpTheme)
    assert_type(HelpTheme().with_(), HelpTheme)
    assert_type(CustomTheme.dark(), CustomTheme)
    assert_type(CustomTheme.light(), CustomTheme)
    assert_type(CustomTheme().with_(), CustomTheme)


@pytest.mark.parametrize(("preset", "foreground"), [("dark", "cyan"), ("light", "blue")])
def test_help_theme_subclass_can_customize_presets(preset: str, foreground: str) -> None:
    theme = getattr(PresetTheme, preset)()

    assert type(theme) is PresetTheme
    assert theme.metavar == Style(fg=foreground)
    assert theme.label == "default"
    assert getattr(theme, "heading") == getattr(getattr(HelpTheme, preset)(), "heading")


def test_style():
    text = "hi there"
    kwargs = dict(fg=Color.green, bold=True, blink=True)
    assert Style(**kwargs)(text) == click.style(text, **kwargs)


def test_unsupported_style_args_are_ignored_in_click_7():
    Style(overline=True, italic=True, strikethrough=True)


def test_color_class():
    # Check values of some attributes
    assert Color.red == "red"
    assert Color.bright_blue == "bright_blue"

    # Check it's not instantiable
    with pytest.raises(Exception, match="it's not instantiable"):
        Color()

    # Check only __dunder__ fields are settable
    Color.__annotations__ = "whatever"
    with pytest.raises(Exception, match="you can't set attributes on this class"):
        Color.red = "blue"

    # Test __contains__
    assert "red" in Color
    assert "pippo" not in Color

    # Test Color.asdict()
    d = Color.asdict()
    for k, v in d.items():
        assert k in Color
        assert Color[k] == v


def test_style_is_hashable_after_calling():
    s = Style(fg="red")
    hash(s)  # no exception
    s("ciao")
    hash(s)  # still hashable
