import pytest

from cloup._util import check_positive_int, make_repr


def test_make_repr():
    expected_repr = "list('arg', name='Alan', surname='Turing')"
    n = len(expected_repr)
    r = make_repr([], 'arg', name='Alan', surname='Turing',
                  _line_len=n)
    assert r == expected_repr

    r = make_repr([], 'arg', name='Alan', surname='Turing',
                  _line_len=n - 1, _indent=3)
    assert r == ("list(\n"
                 "   'arg',\n"
                 "   name='Alan',\n"
                 "   surname='Turing'\n"
                 ")")


def test_check_positive_int():
    check_positive_int(1, 'name')
    with pytest.raises(ValueError):
        check_positive_int(0, 'name')
    with pytest.raises(ValueError):
        check_positive_int(-1, 'name')
    with pytest.raises(TypeError):
        check_positive_int(None, 'name')
    with pytest.raises(TypeError):
        check_positive_int(1.23, 'name')
