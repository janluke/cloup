#!/usr/bin/env python
"""
Tests for `cloup` package.
"""
from click.testing import CliRunner

from tests.example import cli

expected_help = """
Usage: clouptest [OPTIONS] ARG

  A CLI that does nothing.

Option group A:
  This is a useful description of group A
  --a1 TEXT  1st option of group A
  --a2 TEXT  2nd option of group A
  --a3 TEXT  3rd option of group A

Option group B:
  --b1 TEXT  1st option of group B
  --b2 TEXT  2nd option of group B
  --b3 TEXT  3rd option of group B

Other options:
  --opt1 TEXT  an uncategorized option
  --opt2 TEXT  another uncategorized option
  --help       Show this message and exit.
"""

def test_cloup():
    runner = CliRunner()
    result = runner.invoke(cli, args=('--help',))
    assert result.exit_code == 0
    assert result.output.strip() == expected_help.strip()


