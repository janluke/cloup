from cloup._util import make_repr


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
