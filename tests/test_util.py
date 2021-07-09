import pytest

from cloup._util import check_positive_int, coalesce, first_bool, make_repr


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


def test_first_bool():
    assert first_bool(0, 1, None, '', [], False, True) is False
    assert first_bool(0, 1, None, '', [], True, False) is True
    with pytest.raises(StopIteration):
        first_bool(1, 2, '', [], None)


def test_coalesce():
    assert coalesce() is None
    assert coalesce(None, None, None) is None
    for expected in [0, '', [], False, 123]:
        assert coalesce(None, None, expected, True, 12) == expected
