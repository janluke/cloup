"""
Example of options groups, "nested style" (recommended).

The decorator @option_group() is overloaded with two signatures.
Basically, you can specify the optional help string either:

1) as keyword argument, after the options
    @option_group(name: str,
                  *options: Option,
                  help: Optional[str] = None
                  constraint: Optional[Constraint] = None)

2) as 2nd positional argument, before the options

    @option_group(name: str,
                  help: str,
                  *options: Option,
                  constraint: Optional[Constraint] = None)

ATTENTION: this is NOT and doesn't want to be a "meaningful" example!
My goal here is to show you different ways of using the API in a compact way
and give you a file that you can run to see how the help is printed out with
different settings.
"""
from pprint import pprint

import click
from click import Choice

import cloup
from cloup import option, option_group
from cloup.constraints import (
    Equal, If, RequireAtLeast, RequireExactly, constraint, mutually_exclusive,
)


@cloup.command(name='cloup', show_constraints=True)
@click.argument('arg', required=False)
@option_group(
    'First group title',
    "this is a very long description of the option group. I don't think this is "
    "needed very often; still, if you want to provide it, you can pass it as 2nd "
    "positional argument or as keyword argument 'help' after all options.",
    option('--one', help='a 1st cool option'),
    option('--two', help='a 2nd cool option'),
    option('--three', help='a 3rd cool option'),
    constraint=RequireAtLeast(1),
)
@option_group(
    'Second group name',
    option('--four', help='a 4th cool option'),
    option('--five', help='a 5th cool option'),
    option('--six', help='a 6th cool option'),
    constraint=If('three', then=RequireExactly(1)),  # conditional constraint
)
@option('--seven', help='an uncategorized option', type=Choice(['foo', 'bar']))
@option('--eight', help='second uncategorized option')
@constraint(mutually_exclusive, ['one', 'two'])
@constraint(If(Equal('one', '123'), then=RequireExactly(1)), ['seven', 'six'])
def main(**kwargs):
    """A test program for cloup."""
    pprint(kwargs, indent=3)


if __name__ == '__main__':
    main()
