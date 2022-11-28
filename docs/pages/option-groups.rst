Option groups
=============

.. highlight:: python

The @option_group decorator
---------------------------
The recommended way of defining option groups is through the
:func:`~cloup.option_group` decorator. This decorator is overloaded with two
signatures that only differ by how you provide the optional ``help`` argument::

    # help as keyword argument
    @option_group(title, *options, help=None, ...)

    # help as 2nd positional argument
    @option_group(title, help, *options, ...)

Here's the full list of parameters:

- **title** --
  title of the help section describing the option group

- **\*options** --
  an arbitrary number of decorators like those returned by ``cloup.option`` and
  ``click.option``. Since v0.9, each decorator can add even multiple options in
  a row. This was introduced to support constraints as decorators

- **help** --
  an optional description shown below the title; can be provided as keyword
  argument or 2nd positional argument

- **constraint** --
  an optional instance of Constraint (see :doc:`constraints` for more info);
  a description of the constraint will be shown between squared brackets
  aside the option group title (or below it if too long)

- **hidden** --
  if True, the option group and all its options are hidden from the help page
  (all contained options will have their hidden attribute set to True).

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        import cloup
        from cloup import option_group, option
        from cloup.constraints import RequireAtLeast

        @cloup.command()
        @option_group(
            "Input options",
            option("--one", help="1st input option"),
            option("--two", help="2nd input option"),
            option("--three", help="3rd input option"),
        )
        @option_group(
            "Output options",
            "This is a an optional description of the option group.",
            option("--four / --no-four", help="1st output option"),
            option("--five", help="2nd output option"),
            option("--six", help="3rd output option"),
            constraint=RequireAtLeast(1),
        )
        # The following will be shown (with --help) under "Other options"
        @option("--seven", help="1st uncategorized option")
        @option("--height", help="2nd uncategorized option")
        def cli(**kwargs):
            """A CLI that does nothing."""
            print(kwargs)

        cli()

.. tabbed:: Generated help

    .. code-block:: none

        Usage: clouptest [OPTIONS]

          A CLI that does nothing.

        Input options:
          --one TEXT          1st input option
          --two TEXT          2nd input option
          --three TEXT        3rd input option

        Output options: [at least 1 required]
          This is a an optional description of the option group.
          --four / --no-four  1st output option
          --five TEXT         2nd output option
          --six TEXT          3rd output option

        Other options:
          --seven TEXT        1st uncategorized option
          --height TEXT       2nd uncategorized option
          --help              Show this message and exit.

Options that are not assigned to an option group are included is the so called
**default option group**, which is shown for last in the ``--help``.
This group is titled "Other options" unless it is the only option group, in
which case ``cloup.Command`` behaves like a normal ``click.Command``,
naming it just "Options".

In the example above, I used the :func:`cloup.option` decorator to define options
but that's not required: you can use :func:`click.option` or any other decorator
that acts like it. Nonetheless:

.. admonition:: Tip: prefer Cloup decorators over Click ones
    :class: tip

    Cloup provides detailed type hints for (almost) all arguments you can pass
    to parameter and command decorators. This translates to a better
    **IDE support**, i.e. better auto-completion and error detection.

.. _aligned-vs-nonaligned-group:

Aligned vs non-aligned groups
-----------------------------
By default, all option group help sections are **aligned**, meaning that they
share the same column widths. Many people find this visually pleasing and this
is also the default behavior of ``argparse``.

Nonetheless, if some of your option groups have shorter options, alignment may
result in a lot of wasted space and definitions quite far from option names,
which is bad for readability. See this biased example to compare the two modes:

.. tabbed:: Aligned

    .. code-block:: none

        Usage: clouptest [OPTIONS]

          A CLI that does nothing.

        Input options:
          --one TEXT                   This description is more likely to be wrapped
                                       when aligning.
          --two TEXT                   This description is more likely to be wrapped
                                       when aligning.
          --three TEXT                 This description is more likely to be wrapped
                                       when aligning.

        Output options:
          --four                       This description is more likely to be wrapped
                                       when aligning.
          --five TEXT                  This description is more likely to be wrapped
                                       when aligning.
          --six TEXT                   This description is more likely to be wrapped
                                       when aligning.

        Other options:
          --seven [a|b|c|d|e|f|g|h|i]  First uncategorized option.
          --height TEXT                Second uncategorized option.
          --help                       Show this message and exit.

.. tabbed:: Non-aligned

    .. code-block:: none

        Usage: clouptest [OPTIONS]

          A CLI that does nothing.

        Input options:
          --one TEXT    This description is more likely to be wrapped when aligning.
          --two TEXT    This description is more likely to be wrapped when aligning.
          --three TEXT  This description is more likely to be wrapped when aligning.

        Output options:
          --four       This description is more likely to be wrapped when aligning.
          --five TEXT  This description is more likely to be wrapped when aligning.
          --six TEXT   This description is more likely to be wrapped when aligning.

        Other options:
          --seven [a|b|c|d|e|f|g|h|i]  First uncategorized option.
          --height TEXT                Second uncategorized option.
          --help                       Show this message and exit.

In Cloup, you can format each option group independently from each other
setting the ``@command`` parameter ``align_option_groups=False``.
Since v0.8.0, this parameter is also available as a ``Context`` setting::

    from cloup import Context, group

    CONTEXT_SETTINGS = Context.settings(
        align_option_groups=False,
        ...
    )

    @group(context_settings=CONTEXT_SETTINGS)
    def main():
        pass

.. note::
    The problem of aligned groups can sometimes be solved decreasing the
    :class:`HelpFormatter` parameter ``col1_max_width``, which defaults to 30.


Alternative APIs
----------------

Option groups without nesting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
While I largely prefer ``@option_group``, you may not like the additional level
of indentation it requires. In that case, you may prefer the following way
of defining option groups:

.. code-block:: python

    from cloup import OptionGroup
    from cloup.constraints import SetAtLeast

    # OptionGroup takes all arguments of @option_group but *options
    input_grp = OptionGroup(
        'Input options', help='This is a very useful description of the group'
    )
    output_grp = OptionGroup('Output options',  constraint=SetAtLeast(1))

    @cloup.command()
    @input_grp.option('--one')
    @input_grp.option('--two')
    @output_grp.option('--three')
    @output_grp.option('--four')
    def cli_flat(one, two, three, four):
        """A CLI that does nothing."""
        print(kwargs)

The above notation is just syntax sugar on top of ``@cloup.option``:

.. code-block:: python

    @input_grp.option('--one')
    # is equivalent to:
    @cloup.option('--one', group=input_grp)


Option groups without decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For some reason, you may need to work at a lower level, by passing parameters
to a ``Command`` constructor. In that case you can use :class:`cloup.Option`
(or the alias ``GroupedOption``)::

    from cloup import Command, Option, OptionGroup

    output_opts = OptionGroup("Output options")

    params = [
        Option('--verbose', is_flag=True, group=output_opts),
        ...
    ]

    cmd = Command(..., params=params, ...)


Reusing/modularizing option groups
----------------------------------
Some people have asked how to reuse option groups in multiple commands and how
to put particularly long option groups in their own files. This is easy if you
know how Python decorator works. First, you store the decorator returned by
``option_group`` (called without a ``@``) in a variable::

    from cloup import option_group

    output_options = option_group(
        "Output options",
        option(...),
        option(...),
        ...
    )

Then you can use the decorator as many times as you want::

    @command()
    # other decorators...
    @output_options
    # other decorators ...
    def foo()
        ...

Of course, if ``output_options`` is defined in a different file, don't forget to
import it!

.. admonition:: Terminology-nazi note

    It's worth noting that ``output_options`` in the example above is **not**
    an option group, it's just a function that recreate the same ``OptionGroup``
    object and all its options every time it is called. So, technically, you're
    not "reusing an option group".


How it works
------------
This feature is implemented simply by annotating each option with an additional
attribute ``group`` of type ``Optional[OptionGroup]``. Unless the option is of
class ``cloup.Option``, this ``group`` attribute is added and set by monkey-patching.

When the ``Command`` is instantiated, it groups all options by their ``group``
attribute. Options that don't have a ``group`` attribute (or have it set to
``None``) are stored in the "default option group" (together with ``--help``).

In order to show option groups in the command help, ``OptionGroupMixin``
"overrides" ``Command.format_options``.


Feature support
---------------

This features depends on two mixins:

- (*required*) :class:`~cloup.OptionGroupMixin`
- (*optional*) :class:`~cloup.ConstraintMixin`, if you want to use constraints.

.. admonition:: New!
    :class: tip

    Since Cloup v0.14.0, ``cloup.Group`` supports option groups and constraints too.
