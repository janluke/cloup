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
from click import Choice

import cloup
from cloup import option, option_group
from cloup.constraints import If, SetAtLeast, check_constraint, mutually_exclusive


@cloup.command(name='cloup')
@click.argument('arg', required=False)
@option_group(
    'First group title',
    "This is a very long description of the option group. I don't think this is "
    "needed very often; still, if you want to provide it, you can pass it as 2nd "
    "positional argument or as keyword argument 'help' after all options.",
    option('--one', type=int, help='a 1st cool option'),
    option('--two', help='a 2nd cool option'),
    option('--three', help='a 3rd cool option'),
    constraint=SetAtLeast(1),
)
@option_group(
    'Second group name',
    option('--four', help='a 4th cool option'),
    option('--five', help='a 5th cool option'),
    option('--six', help='a 6th cool option'),
    constraint=If('three').then(SetAtLeast(1)),
)
@option('--seven', help='first uncategorized option', type=Choice('yes no ask'.split()))
@option('--eight', help='second uncategorized option')
def main(**kwargs):
    """ A CLI that does nothing. """

    # Constraints can be used inside a callback. The [ctx] argument is optional.
    mutually_exclusive.check(['one', 'six'])

    # The function check_constraint exists for the only reason to make crystal
    # clear what you are doing. It may be "weird" to call check on some
    # constraints, because some of them are named as "commands" to the CLI user
    check_constraint(
        SetAtLeast(1), on=['one', 'six'])

    pprint(kwargs, indent=3)


if __name__ == '__main__':
    main()
