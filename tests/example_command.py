# flake8: noqa E128
from typing import cast

import click

import cloup
from cloup import Command, HelpFormatter, argument, option, option_group
from cloup.constraints import AcceptAtMost, If, RequireAtLeast


def make_example_command(
    align_option_groups: bool,
    tabular_help: bool = True,
) -> Command:
    @cloup.command(
        'clouptest',
        align_option_groups=align_option_groups,
        formatter_settings=HelpFormatter.settings(
            width=80,
            col2_min_width=30 if tabular_help else 80,
        ),
        epilog='Made with love by Gianluca.'
    )
    @argument("arg_one", help="This is the description of argument #1.")
    @argument("arg_two", help="This is the description of argument #2.", required=False)
    @argument("arg_three", required=False)
    @option_group(
        'Option group A',
        option('--one', help='The one thing you need to run this command.'),
        option('--two', help='This is long description that should be wrapped into '
                             'multiple lines so that the entire text stays inside '
                             'the allowed width.'),
        option('--three', help='The 3rd option of group A.'),
        help="This is a very useful description of group A. This is a rarely used "
             "feature but, as the others, needs to be tested. I'm making this "
             "unnecessarily long in order to test wrapping.",
        constraint=AcceptAtMost(2)
    )
    @option_group(
        'Option group B',
        'Help as positional argument.',
        option('--four / --no-four', help='The 1st option of group B.'),
        option('--five', help='The 2nd option of group B.', hidden=True),  # hidden option
        option('--six', help='The 3rd option of group B.'),
        constraint=If('three', then=RequireAtLeast(1))
    )
    @option('--seven', help='First uncategorized option.',
            type=click.Choice('yes no ask'.split()))
    @option('--height', help='Second uncategorized option.')
    @option('--nine', help='Third uncategorized option.', hidden=True)
    def cmd(**kwargs):
        """A CLI that does nothing."""
        print(kwargs)

    if tabular_help:
        expected_help = (_TABULAR_ALIGNED_HELP if align_option_groups
                         else _TABULAR_NON_ALIGNED_HELP)
    else:
        expected_help = _LINEAR_HELP

    cmd.expected_help = expected_help   # type: ignore
    return cast(Command, cmd)


_TABULAR_ALIGNED_HELP = """
Usage: clouptest [OPTIONS] ARG_ONE [ARG_TWO] [ARG_THREE]

  A CLI that does nothing.

Positional arguments:
  ARG_ONE               This is the description of argument #1.
  [ARG_TWO]             This is the description of argument #2.
  [ARG_THREE]

Option group A: [at most 2 accepted]
  This is a very useful description of group A. This is a rarely used feature
  but, as the others, needs to be tested. I'm making this unnecessarily long in
  order to test wrapping.
  --one TEXT            The one thing you need to run this command.
  --two TEXT            This is long description that should be wrapped into
                        multiple lines so that the entire text stays inside the
                        allowed width.
  --three TEXT          The 3rd option of group A.

Option group B: [at least 1 required if --three is set]
  Help as positional argument.
  --four / --no-four    The 1st option of group B.
  --six TEXT            The 3rd option of group B.

Other options:
  --seven [yes|no|ask]  First uncategorized option.
  --height TEXT         Second uncategorized option.
  --help                Show this message and exit.

Made with love by Gianluca.
""".strip()

_TABULAR_NON_ALIGNED_HELP = """
Usage: clouptest [OPTIONS] ARG_ONE [ARG_TWO] [ARG_THREE]

  A CLI that does nothing.

Positional arguments:
  ARG_ONE      This is the description of argument #1.
  [ARG_TWO]    This is the description of argument #2.
  [ARG_THREE]

Option group A: [at most 2 accepted]
  This is a very useful description of group A. This is a rarely used feature
  but, as the others, needs to be tested. I'm making this unnecessarily long in
  order to test wrapping.
  --one TEXT    The one thing you need to run this command.
  --two TEXT    This is long description that should be wrapped into multiple
                lines so that the entire text stays inside the allowed width.
  --three TEXT  The 3rd option of group A.

Option group B: [at least 1 required if --three is set]
  Help as positional argument.
  --four / --no-four  The 1st option of group B.
  --six TEXT          The 3rd option of group B.

Other options:
  --seven [yes|no|ask]  First uncategorized option.
  --height TEXT         Second uncategorized option.
  --help                Show this message and exit.

Made with love by Gianluca.
""".strip()

_LINEAR_HELP = """
Usage: clouptest [OPTIONS] ARG_ONE [ARG_TWO] [ARG_THREE]

  A CLI that does nothing.

Positional arguments:
  ARG_ONE
     This is the description of argument #1.

  [ARG_TWO]
     This is the description of argument #2.

  [ARG_THREE]

Option group A: [at most 2 accepted]
  This is a very useful description of group A. This is a rarely used feature
  but, as the others, needs to be tested. I'm making this unnecessarily long in
  order to test wrapping.
  --one TEXT
     The one thing you need to run this command.

  --two TEXT
     This is long description that should be wrapped into multiple lines so that
     the entire text stays inside the allowed width.

  --three TEXT
     The 3rd option of group A.

Option group B: [at least 1 required if --three is set]
  Help as positional argument.
  --four / --no-four
     The 1st option of group B.

  --six TEXT
     The 3rd option of group B.

Other options:
  --seven [yes|no|ask]
     First uncategorized option.

  --height TEXT
     Second uncategorized option.

  --help
     Show this message and exit.

Made with love by Gianluca.
""".strip()


if __name__ == '__main__':
    make_example_command(align_option_groups=False, tabular_help=True)(
        ['--help'], prog_name='clouptest'
    )
