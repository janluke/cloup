# flake8: noqa E128
import click

import cloup
from cloup import option, option_group
from cloup.constraints import If, RequireAtLeast


def make_example_command(align_option_groups):
    @cloup.command(
        'clouptest',
        align_option_groups=align_option_groups,
        context_settings={'terminal_width': 80})
    @option_group(
        'Option group A',
        option('--one', help='1st option of group A'),
        option('--two', help='2nd option of group A'),
        option('--three', help='3rd option of group A'),
        help='This is a very useful description of group A')
    @option_group(
        'Option group B', 'Help as positional argument',
        option('--four / --no-four', help='1st option of group B'),
        option('--five', help='2nd option of group B', hidden=True),  # hidden option
        option('--six', help='3rd option of group B'),
        constraint=If('three', then=RequireAtLeast(1)))
    @option('--seven', help='first uncategorized option',
            type=click.Choice('yes no ask'.split()))
    @option('--height', help='second uncategorized option')
    @option('--nine', help='second uncategorized option', hidden=True)
    def cmd(**kwargs):
        """ A CLI that does nothing. """
        print(kwargs)

    cmd.expected_help = (_EXPECTED_ALIGNED_HELP if align_option_groups
                         else _EXPECTED_NON_ALIGNED_HELP)
    return cmd


_EXPECTED_ALIGNED_HELP = """
Usage: clouptest [OPTIONS]

  A CLI that does nothing.

Option group A:
  This is a very useful description of group A
  --one TEXT            1st option of group A
  --two TEXT            2nd option of group A
  --three TEXT          3rd option of group A

Option group B [at least 1 required if --three is set]:
  Help as positional argument
  --four / --no-four    1st option of group B
  --six TEXT            3rd option of group B

Other options:
  --seven [yes|no|ask]  first uncategorized option
  --height TEXT         second uncategorized option
  --help                Show this message and exit.
""".strip()

_EXPECTED_NON_ALIGNED_HELP = """
Usage: clouptest [OPTIONS]

  A CLI that does nothing.

Option group A:
  This is a very useful description of group A
  --one TEXT    1st option of group A
  --two TEXT    2nd option of group A
  --three TEXT  3rd option of group A

Option group B [at least 1 required if --three is set]:
  Help as positional argument
  --four / --no-four  1st option of group B
  --six TEXT          3rd option of group B

Other options:
  --seven [yes|no|ask]  first uncategorized option
  --height TEXT         second uncategorized option
  --help                Show this message and exit.
""".strip()

if __name__ == '__main__':
    make_example_command(align_option_groups=True)(
        ['--help'], prog_name='clouptest'
    )
