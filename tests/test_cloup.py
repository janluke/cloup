#!/usr/bin/env python
"""
Tests for `cloup` package.
"""
from click.testing import CliRunner

import cloup
from cloup import (
    option_group,
    option
)
from tests.example import cli

expected_help = """
Usage: clouptest [OPTIONS] [ARG]

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

def test_cloup_example():
    runner = CliRunner()
    result = runner.invoke(cli, args=('--help',))
    assert result.exit_code == 0
    assert result.output.strip() == expected_help.strip()


def test_hidden_option():
    @cloup.command()
    @option_group('group', [
        option('--opt1', hidden=True),
        option('--opt2')
    ])
    def cli(opt1, opt2):
        return 0

    result = CliRunner().invoke(cli, args=('--help',))
    assert result.exit_code == 0
    assert '--opt1' not in result.output
    assert '--opt2' in result.output, result.output
