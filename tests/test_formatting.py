import pytest

from cloup.formatting import truncate_text


TEXT = "1234 678 012345"
@pytest.mark.parametrize('start, end, expected', [    # noqa: E302
    pytest.param(0,  7,  "",            id="0-7"),
    pytest.param(7,  11, "1234...",     id="7-11"),
    pytest.param(11, 15, "1234 678...", id="11-15"),
    pytest.param(15, 17, TEXT,          id="15+"),
])
def test_truncate_text(start, end, expected):
    for i in range(start, end):
        assert truncate_text(TEXT, i) == expected, i
