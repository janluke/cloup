from functools import partial

import pytest

from cloup.formatting.sep import (
    Hline, RowSepIf, count_multiline_rows, multiline_rows_are_at_least
)

# Use the same widths for both columns
cols_width = 30
col_widths = (cols_width, cols_width)
col_spacing = 2

# We'll use these in many tests (a = above_limit, b = below_limit)
above_limit = 'a' * (cols_width + 1)
below_limit = 'b' * cols_width
aa = (above_limit, above_limit)
ab = (above_limit, below_limit)
ba = (below_limit, above_limit)
bb = (below_limit, below_limit)


def test_count_multiline_rows():
    count = partial(count_multiline_rows, col_widths=col_widths)
    assert count([bb]) == 0
    assert count([ba]) == 1
    assert count([ab]) == 1
    assert count([aa]) == 1
    assert count([bb, ba, ab, aa]) == 3
    with pytest.raises(Exception):
        count([tuple('1234')])  # len(row) > len(col_widths)


class TestMultilineRowsAreAtLeast:
    @pytest.mark.parametrize('bad_value', [0, 0.0, -1, -1.4, 1.1, 11.0])
    def test_args_validation(self, bad_value):
        with pytest.raises(ValueError):
            multiline_rows_are_at_least(bad_value)

    def test_with_count(self):
        at_least_2_multiline_rows = partial(multiline_rows_are_at_least(2),
                                            col_widths=(30, 30), col_spacing=2)
        assert at_least_2_multiline_rows([ab, bb, bb, ba])
        assert at_least_2_multiline_rows([ab, bb, bb, ba, aa])
        assert not at_least_2_multiline_rows([bb, bb, bb])

    def test_with_percentage(self):
        at_least_half_multiline_rows = partial(multiline_rows_are_at_least(.5),
                                               col_widths=(30, 30), col_spacing=2)
        assert at_least_half_multiline_rows([
            bb, bb, bb,
            aa, ab, ba,
        ])
        assert at_least_half_multiline_rows([
            bb, bb, bb,
            aa, ab, ba, aa, ab
        ])
        assert not at_least_half_multiline_rows([
            bb, bb, bb, bb,
            aa, ab, ba,
        ])
        assert not at_least_half_multiline_rows([bb] * 5)


def test_value_error_if_sep_string_ends_with_newline():
    with pytest.raises(ValueError, match=r"sep must not end with '\\n'"):
        RowSepIf(multiline_rows_are_at_least(1), sep='\n')


def test_Hline():
    assert Hline.solid(5) == "─────"
    assert Hline.dashed(5) == "-----"
    assert Hline.densely_dashed(5) == "╌╌╌╌╌"
    assert Hline.dotted(5) == "┄┄┄┄┄"
    assert Hline('-.')(5) == '-.-.-'
