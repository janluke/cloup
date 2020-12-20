"""
Example of option groups, "flat style".
"""
import click

import cloup
from cloup import OptionGroup, option

# WARNING: don't reuse OptionGroup objects in multiple commands!
_input = OptionGroup('Input options', help='This is a very useful description of the group')
_output = OptionGroup('Output options')


@cloup.command('cloup_flat', align_option_groups=True)
#
@_input.option('-o', '--one', help='1st input option')
@_input.option('--two', help='2nd input option')
@_input.option('--three', help='3rd input option')
#
@_output.option('--four / --no-four', help='1st output option')
@_output.option('--five', help='2nd output option')
@_output.option('--six', help='3rd output option')
#
@option('--seven', help='first uncategorized option',
        type=click.Choice('yes no ask'.split()))
@option('--height', help='second uncategorized option')
def main(**kwargs):
    """ A CLI that does nothing. """
    print(kwargs)


if __name__ == '__main__':
    main()
