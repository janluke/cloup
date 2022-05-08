"""
Show-casing the "Positional arguments" help section.
"""
from pprint import pprint

import cloup
from cloup import option, option_group


@cloup.command(name='cloup', show_constraints=True)
@cloup.argument('input_path', help="Input path")
@cloup.argument('out_path', help="Output path")
@option_group(
    'An option group',
    option('-o', '--one', help='a 1st cool option'),
    option('-t', '--two', help='a 2nd cool option'),
    option('--three', help='a 3rd cool option'),
)
def main(**kwargs):
    """A test program for cloup."""
    pprint(kwargs, indent=3)


if __name__ == '__main__':
    main()

"""
Usage: arguments_with_help.py [OPTIONS] INPUT_PATH OUT_PATH

  A test program for cloup.

Positional arguments:
  INPUT_PATH      Input path
  OUT_PATH        Output path

An option group:
  -o, --one TEXT  a 1st cool option
  -t, --two TEXT  a 2nd cool option
  --three TEXT    a 3rd cool option

Other options:
  --help          Show this message and exit.
"""
