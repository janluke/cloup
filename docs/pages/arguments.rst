Arguments with ``help``
=======================

If you've used Click before, you probably know that:

    ``click.argument()`` does not take a help parameter. This is to follow the
    general convention of Unix tools of using arguments for only the most
    necessary things, and to document them in the command help text by referring
    to them by name.

Cloup doesn't force the Unix convention on you. ``cloup.argument`` takes an
optional ``help`` parameter. If you pass a non-empty string to at least one of
the arguments of a command, Cloup will print a "Positional arguments" section
just below the command description.

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        from pprint import pprint
        import cloup
        from cloup import option, option_group

        @cloup.command()
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

        main()

.. tabbed:: Generated help

    .. code-block:: none

        Usage: example [OPTIONS] INPUT_PATH OUT_PATH

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
