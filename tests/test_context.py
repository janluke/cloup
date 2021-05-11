from unittest.mock import Mock

import pytest

import cloup
from cloup import Context
from tests.util import parametrize


@parametrize(
    ['ctx_arg_name', 'formatter_arg_name'],
    pytest.param('terminal_width', 'width', id='width'),
    pytest.param('max_content_width', 'max_width', id='max_width'),
)
@parametrize(
    ['ctx_arg_value', 'formatter_arg_value', 'should_warn'],
    pytest.param(80, None, False, id='only_ctx'),
    pytest.param(None, 90, False, id='only_formatter'),
    pytest.param(80, 90, True, id='both'),
)
def test_warning_is_raised_iff_arg_is_provided_both_as_context_and_formatter_arg(
    ctx_arg_name, formatter_arg_name, ctx_arg_value, formatter_arg_value, should_warn
):
    kwargs = {
        ctx_arg_name: ctx_arg_value,
        "formatter_settings": {formatter_arg_name: formatter_arg_value}
    }

    with pytest.warns(None) as warns:
        Context(command=Mock(), **kwargs)
    if should_warn:
        assert len(warns) == 1
        warning = warns[0]
        assert warning.category is UserWarning
        assert 'You provided both' in str(warning.message)
    else:
        assert len(warns) == 0


@parametrize(
    ['ctx_arg_name', 'formatter_arg_name'],
    pytest.param('terminal_width', 'width', id='width'),
    pytest.param('max_content_width', 'max_width', id='max_width'),
)
def test_warning_suppression(ctx_arg_name, formatter_arg_name):
    kwargs = {
        ctx_arg_name: 80, "formatter_settings": {formatter_arg_name: 90}
    }
    cloup.warnings.formatter_settings_conflict = False
    with pytest.warns(None) as warns:
        Context(command=Mock(), **kwargs)
    cloup.warnings.formatter_settings_conflict = True
    assert len(warns) == 0


def test_context_settings_creation():
    assert Context.settings() == {}
    assert Context.settings(
        resilient_parsing=False, align_sections=True, formatter_settings={'width': 80}
    ) == dict(
        resilient_parsing=False, align_sections=True, formatter_settings={'width': 80}
    )
