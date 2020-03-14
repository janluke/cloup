import click

import cloup
from cloup import OptionGroup, option, option_group


# ==============
#  Nested style.
#  option_group() is overloaded:
#    @option_group(name: str, *options, help: Optional[str] = None)
#    @option_group(name: str, help: str, *options)
@cloup.command('clouptest')
@option_group('Input options',
    "This is a very long description of the option group. I don't think this is "
    "needed very often; still, if you want to provide it, you can pass it as 2nd "
    "positional argument or as keyword argument 'help' after all options.",
    option('-o', '--one', help='1st input option'),
    option('--two', help='2nd input option'),
    option('--three', help='3rd input option')
)
@option_group('Output options',
    option('--four / --no-four', help='1st output option'),
    option('--five', help='2nd output option'),
    option('--six', help='3rd output option'),
    # help='You can also pass the help as keyword argument after the options.'
)
@option('--seven', help='first uncategorized option', type=click.Choice('yes no ask'.split()))
@option('--height', help='second uncategorized option')
def cli_nested(**kwargs):
    """ A CLI that does nothing. """
    print(kwargs)


# ==============
#  Flat style
#  WARNING: don't reuse OptionGroup objects in multiple commands!
_input = OptionGroup('Input options', help='This is a very useful description of the group')
_output = OptionGroup('Output options')


@cloup.command('clouptest', align_option_groups=True)
@_input.option('-o', '--one', help='1st input option')
@_input.option('--two', help='2nd input option')
@_input.option('--three', help='3rd input option')
@_output.option('--four / --no-four', help='1st output option')
@_output.option('--five', help='2nd output option')
@_output.option('--six', help='3rd output option')
@option('--seven', help='first uncategorized option', type=click.Choice('yes no ask'.split()))
@option('--height', help='second uncategorized option')
def cli_flat(**kwargs):
    """ A CLI that does nothing. """
    print(kwargs)


if __name__ == '__main__':
    cli_nested('--help'.split())
