import inspect

import click
import pytest

from cloup.styling import Color, HelpTheme, Style


def test_help_theme_copywith():
    s1, s2 = Style(), Style()
    r1, r2 = Style(), Style()
    theme = HelpTheme(heading=s1, col1=s2).with_(col1=r1, col2=r2)
    assert theme == HelpTheme(heading=s1, col1=r1, col2=r2)


def test_help_theme_copywith_takes_the_same_parameters_of_constructor():
    def get_param_names(func):
        params = inspect.signature(func).parameters
        return list(params.keys())

    constructor_params = get_param_names(HelpTheme)
    method_params = get_param_names(HelpTheme.with_)[1:]  # skip self
    assert method_params == constructor_params


def test_help_theme_default_themes():
    assert isinstance(HelpTheme.dark(), HelpTheme)
    assert isinstance(HelpTheme.light(), HelpTheme)


def test_style():
    text = 'hi there'
    kwargs = dict(fg=Color.green, bold=True, blink=True)
    assert Style(**kwargs)(text) == click.style(text, **kwargs)


def test_unsupported_style_args_are_ignored_in_click_7():
    Style(overline=True, italic=True, strikethrough=True)


def test_Color():
    assert Color.red == 'red'
    assert Color.bright_blue == 'bright_blue'

    with pytest.raises(Exception, match="it's not instantiable"):
        Color()
    with pytest.raises(Exception, match="you can't set attributes on this class"):
        Color.red = 'blue'

    assert 'red' in Color
    assert 'pippo' not in Color
    d = Color.asdict()
    for k, v in d.items():
        assert k in Color
        assert Color[k] == v
