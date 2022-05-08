"""
Example of options groups, "nested style" (recommended).

NOTE: the goal of this example is to showcase Cloup's option groups and constraint API
    in a compact way; the example is neither meaningful nor represents a good usage
    of the library (in fact, you should always design your CLI so that it doesn't
    need constraints).
"""
from pprint import pprint

from click import Choice

import cloup
from cloup import option, option_group
from cloup.constraints import (
    Equal, If, RequireAtLeast, RequireExactly, constraint, mutually_exclusive,
)


@cloup.command(name='cloup', show_constraints=True)
@cloup.argument('input_path')
@cloup.argument('out_path')
@option_group(
    'First group title',
    "This is a very long description of the option group. I don't think this is "
    "needed very often; still, if you want to provide it, you can pass it as 2nd "
    "positional argument or as keyword argument 'help' after all options.",
    option('-o', '--one', help='a 1st cool option'),
    option('-t', '--two', help='a 2nd cool option'),
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
# Usage of @constraint
@constraint(mutually_exclusive, ['one', 'two'])
@constraint(
    If(Equal('one', '123'), then=RequireExactly(1)),
    ['seven', 'six']
)
def main(**kwargs):
    """A test program for cloup."""
    pprint(kwargs, indent=3)


if __name__ == '__main__':
    main()
