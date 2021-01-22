from click import Argument, Option

from cloup.constraints.util import get_param_label, param_value_is_set
from tests.util import flag_opt, mark_parametrize, multi_opt


def test_get_param_label():
    assert get_param_label(Argument(['arg'])) == 'ARG'
    assert get_param_label(Option(['--opt'])) == '--opt'
    assert get_param_label(Option(['--opt', '-o'])) == '--opt'
    assert get_param_label(Option(['-o', '--opt'])) == '--opt'
    assert get_param_label(Option(['-o/-O', '--opt/--no-opt'])) == '--opt'


@mark_parametrize(
    ['param',            'value',  'expected'],
    (Argument(['arg']),  None,     False),
    (Argument(['arg']),  'bu',     True),
    (Option(['-o']),     None,     False),
    (Option(['-o']),     'bu',     True),
    (flag_opt('-o'),     False,    False),
    (flag_opt('-o'),     True,     True),
    (multi_opt('-o'),    (),       False),
    (multi_opt('-o'),    (1, 2),   True),
)
def test_param_value_is_set(param, value, expected):
    assert param_value_is_set(param, value) == expected
