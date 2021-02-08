"""
Example of option groups, "flat style".
"""
import click

import cloup
from cloup import OptionGroup, option
from cloup.constraints import If, RequireAtLeast, mutually_exclusive

_input = OptionGroup(
    'Input options',
    help='This is a very useful description of the group',
    constraint=mutually_exclusive,
)
_output = OptionGroup(
    'Output options',
    constraint=If('three', then=RequireAtLeast(1)),
)


@cloup.command('cloup_flat', align_option_groups=True)
# Input options
@_input.option('-o', '--one', help='1st input option')
@_input.option('--two', help='2nd input option')
@_input.option('--three', help='3rd input option')
# Output options
@_output.option('--four', help='1st output option')
@_output.option('--five', help='2nd output option')
@_output.option('--six', help='3rd output option')
# Other options
@option('--seven', help='first uncategorized option',
        type=click.Choice('yes no ask'.split()))
@option('--height', help='second uncategorized option')
def main(**kwargs):
    """ A CLI that does nothing. """
    print(kwargs)


if __name__ == '__main__':
    main()
