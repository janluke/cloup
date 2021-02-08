from click import Argument, Option

from cloup.constraints.common import get_param_label, param_value_is_set
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
