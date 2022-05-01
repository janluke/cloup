import pytest

from cloup.location import join_module_paths, parent_module_of


@pytest.mark.parametrize(
    ("inputs", "expected"),
    [
        (["a.b", "c.d"], "a.b.c.d"),
        (["a.b", ".c"], "a.c"),
        (["a.b.c.d.e", "...f"], "a.b.f"),
    ]
)
def test_join_module_paths(inputs, expected):
    assert join_module_paths(*inputs) == expected


def test_parent_module_of():
    assert parent_module_of("a.b.c") == "a.b"
