"""
Example of options groups, "nested style" (recommended).

The decorator @option_group() is overloaded with two signatures:

   1) @option_group(name: str,
                    *options: GroupedOption,
                    help: Optional[str] = None
                    **kwargs)

   2) @option_group(name: str,
                    help: str,
                    *options: GroupedOption,
                    **kwargs)

Basically, you can specify the optional help string either
- as 2nd positional
- or as keyword argument after the options
"""
from pprint import pprint

import click

import cloup
from cloup import option, option_group


@cloup.command('cloup')
@option_group(
    'Input options',
    "This is a very long description of the option group. I don't think this is "
    "needed very often; still, if you want to provide it, you can pass it as 2nd "
    "positional argument or as keyword argument 'help' after all options.",
    option('--one', help='1st input option'),
    option('--two', help='2nd input option'),
    option('--three', help='3rd input option'),
)
@option_group(
    'Output options',
    option('--four', help='1st output option'),
    option('--five', help='2nd output option'),
    option('--six', help='3rd output option'),
    # help='You can also pass the help as keyword argument after the options.',
)
@option('--seven', help='first uncategorized option', type=click.Choice('yes no ask'.split()))
@option('--height', help='second uncategorized option')
def main(**kwargs):
    """ A CLI that does nothing. """
    pprint(kwargs, indent=2)


if __name__ == '__main__':
    main()
