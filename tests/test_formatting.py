"""
Tip: in your editor, set a ruler at 80 characters.
"""
import inspect
from textwrap import dedent
from typing import Optional

import click
import pytest

from cloup import HelpFormatter
from cloup.formatting import HelpSection, unstyled_len
from cloup.formatting.sep import (
    Hline, RowSepIf, RowSepPolicy, multiline_rows_are_at_least
)
from cloup.styling import HelpTheme, Style
from cloup.typing import Possibly
from tests.util import parametrize

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor."
ROWS = [
    ('-l, --long-option-name TEXT', LOREM),
    ('--another-option INT', LOREM),
    ('--short', LOREM),
]


def test_write_dl_with_col1_max_width_equal_to_longest_col1_value():
    formatter = HelpFormatter(width=80, col1_max_width=len(ROWS[0][0]))
    formatter.current_indent = 4
    expected = """
    -l, --long-option-name TEXT  Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    --another-option INT         Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    --short                      Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    """[1:-4]
    formatter.write_dl(ROWS)
    assert formatter.getvalue() == expected


def test_formatter_excludes_rows_exceeding_col1_max_width_from_col1_width_computation():
    formatter = HelpFormatter(width=80, col1_max_width=len('--short'))
    formatter.current_indent = 4
    expected = """
    -l, --long-option-name TEXT
             Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
             eiusmod tempor.
    --another-option INT
             Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
             eiusmod tempor.
    --short  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
             eiusmod tempor.
    """[1:-4]
    formatter.write_dl(ROWS)
    assert formatter.getvalue() == expected


def test_col2_min_width():
    formatter = HelpFormatter(width=80)
    formatter.current_indent = 4
    formatter.col2_min_width = (
        formatter.available_width - len(ROWS[0][0]) - formatter.col_spacing)
    expected = """
    -l, --long-option-name TEXT  Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    --another-option INT         Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    --short                      Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    """[1:-4]
    formatter.write_dl(ROWS)
    assert formatter.getvalue() == expected

    formatter.buffer = []
    formatter.col2_min_width += 1
    expected = """
    -l, --long-option-name TEXT
       Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
       tempor.

    --another-option INT
       Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
       tempor.

    --short
       Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
       tempor.
    """[1:-4]
    formatter.write_dl(ROWS)
    assert formatter.getvalue() == expected


def test_value_error_if_row_sep_string_ends_with_newline():
    with pytest.raises(ValueError, match=r"row_sep must not end with '\\n'"):
        HelpFormatter(row_sep='\n')


@parametrize(
    'row_sep',
    pytest.param('-' * (80 - 4), id='string'),
    pytest.param(Hline.dashed, id='SepGenerator'),
)
def test_fixed_row_sep(row_sep):
    formatter = HelpFormatter(row_sep=row_sep, width=80)
    formatter.current_indent = 4
    expected = """
    -l, --long-option-name TEXT  Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    ----------------------------------------------------------------------------
    --another-option INT         Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    ----------------------------------------------------------------------------
    --short                      Lorem ipsum dolor sit amet, consectetur
                                 adipiscing elit, sed do eiusmod tempor.
    """[1:-4]
    formatter.write_dl(ROWS)
    actual = formatter.getvalue()
    assert actual == expected


@parametrize(
    ['policy', 'expected_sep'],  # unless None, expected_sep should end with \n
    # Three of the test rows are "multi-line"
    pytest.param(
        RowSepIf(multiline_rows_are_at_least(3)),
        '',
        id='empty_line'),
    pytest.param(
        RowSepIf(multiline_rows_are_at_least(3), sep=Hline.dashed),
        Hline.dashed(80),
        id='dashed_line'),
    pytest.param(
        RowSepIf(multiline_rows_are_at_least(4)),
        None,
        id='no_sep'),
)
def test_conditional_row_sep(policy: RowSepPolicy, expected_sep: Optional[str]):
    formatter = HelpFormatter(
        width=80, col1_max_width=30, col2_min_width=0, col_spacing=3,
        row_sep=policy,
    )
    rows = [
        ('Longest than 30 characters for sure', 'Short help'),
        ('Longest than 30 characters for sure', 'Another short help'),
        ('Below 30 characters', LOREM),
        ('Short help', 'Short help'),
    ]
    actual_expected_sep = '' if expected_sep is None else (expected_sep + '\n')
    expected = """
Longest than 30 characters for sure
                      Short help
---
Longest than 30 characters for sure
                      Another short help
---
Below 30 characters   Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                      sed do eiusmod tempor.
---
Short help            Short help
    """[1:-4].replace('---\n', actual_expected_sep)

    formatter.write_dl(rows)
    actual = formatter.getvalue()
    assert actual == expected


def test_formatter_settings_creation():
    assert HelpFormatter.settings() == {}
    assert HelpFormatter.settings(
        indent_increment=4, col_spacing=3
    ) == dict(indent_increment=4, col_spacing=3)


def test_settings_signature_matches_HelpFormatter():
    cls_params = dict(inspect.signature(HelpFormatter).parameters)
    settings = dict(inspect.signature(HelpFormatter.settings).parameters)
    assert set(cls_params) == set(settings)
    # Check type annotations
    for name, param in cls_params.items():
        assert settings[name].annotation == Possibly[cls_params[name].annotation], name


def test_write_heading():
    formatter = HelpFormatter(theme=HelpTheme(
        heading=Style(fg='blue', bold=True),
    ))
    formatter.write_heading('Title')
    assert formatter.getvalue() == click.style('Title:', fg='blue', bold=True) + '\n'


def test_write_text_with_styles():
    formatter = HelpFormatter(width=80)
    formatter.current_indent = 4
    WRAPPED = dedent("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat."""[1:])
    INPUT_TEXT = ' '.join(WRAPPED.split())
    indentation = ' ' * formatter.current_indent
    style = Style(fg='yellow')
    EXPECTED = '\n'.join(
        indentation + style(line) for line in WRAPPED.splitlines()
    )
    formatter.write_text(INPUT_TEXT, style=style)
    actual = formatter.getvalue().rstrip()
    for line in actual.splitlines():
        assert unstyled_len(line) <= formatter.width
    assert actual == EXPECTED


def test_write_section_print_long_constraint_on_a_new_line():
    formatter = HelpFormatter(width=72, indent_increment=4)
    section = HelpSection(
        'The heading',
        [('term', 'This is the definition.')],
        help='This is the help.',
        constraint="""
            This is a long constraint description that doesn't fit the line xx.
        """.strip()
    )
    expected = dedent("""
        The heading:
            [This is a long constraint description that doesn't fit the line
            xx.]
            This is the help.
            term  This is the definition.
        """)
    formatter.write_section(section)
    actual = formatter.getvalue()
    assert actual == expected
