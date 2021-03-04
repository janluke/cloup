from functools import partial
from textwrap import dedent

from click import Argument, Option

from cloup.constraints.common import format_param, format_param_list, get_param_label, param_value_is_set
from tests.util import bool_opt, flag_opt, int_opt, mark_parametrize, multi_opt, tuple_opt


@mark_parametrize(
    'param_init,    value,      expected',
    (Argument,      None,       False),
    (Argument,      'bu',       True),
    (Option,        None,       False),
    (Option,        'bu',       True),
    (int_opt,       0,          True),
    (bool_opt,      False,      True),   # non-flag boolean opts are set even if False
    (flag_opt,      False,      False),
    (flag_opt,      True,       True),
    (tuple_opt,     (),         False),
    (tuple_opt,     (1, 2),     True),
    (multi_opt,     (),         False),
    (multi_opt,     (1, 2),     True),
)
def test_param_value_is_set(param_init, value, expected):
    param = param_init(['-o'])
    assert param_value_is_set(param, value) == expected


def test_get_param_label():
    assert get_param_label(Argument(['arg'])) == 'ARG'
    assert get_param_label(Option(['--opt'])) == '--opt'
    assert get_param_label(Option(['--opt', '-o'])) == '--opt'
    assert get_param_label(Option(['-o', '--opt'])) == '--opt'
    assert get_param_label(Option(['-o/-O', '--opt/--no-opt'])) == '--opt'


def test_format_param():
    assert format_param(Argument(['arg'])) == 'ARG'
    assert format_param(Option(['--opt'])) == '--opt'
    assert format_param(Option(['-o'])) == '-o'
    assert format_param(Option(['--opt', '-o'])) == '--opt (-o)'
    assert format_param(Option(['-o', '--opt'])) == '--opt (-o)'
    assert format_param(Option(['-o/-O', '--opt/--no-opt', 'blah'])) == '--opt (-o)'


def test_format_param_list():
    params = [
        Argument(['arg']),
        Option(['--one']),
        Option(['--two', '-t']),
    ]
    expected = (' ARG\n'
                ' --one\n'
                ' --two (-t)\n')
    assert format_param_list(params, indent=1) == expected
