"""
Tip: in your editor, set a ruler at 80 characters.
"""
from textwrap import dedent

import click

from cloup import HelpFormatter
from cloup.formatting import HelpSection, unstyled_len
from cloup.styling import HelpTheme, Style

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


def test_row_sep():
    formatter = HelpFormatter(row_sep='-' * 76 + '\n')
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
    ----------------------------------------------------------------------------
    """[1:-4]
    formatter.write_dl(ROWS)
    assert formatter.getvalue() == expected


def test_formatter_settings_creation():
    assert HelpFormatter.settings() == {}
    assert HelpFormatter.settings(
        width=None, max_width=None,
        indent_increment=4, col_spacing=3
    ) == dict(indent_increment=4, col_spacing=3)


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
