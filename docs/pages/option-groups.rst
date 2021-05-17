
Option groups
=============

.. highlight:: python

The @option_group decorator
---------------------------
The recommended way of defining option groups is through the decorator
:func:`~cloup.option_group`.

.. autofunction:: cloup.option_group

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        import cloup
        from cloup import option_group, option
        from cloup.constraints import SetAtLeast

        @cloup.command('clouptest')
        @option_group(
            "Input options",
            "This is a very long description of the option group. I don't think this is "
            "needed very often; still, if you want to provide it, you can pass it as 2nd "
            "positional argument or as keyword argument 'help' after all options.",
            option('-o', '--one', help='1st input option'),
            option('--two', help='2nd input option'),
            option('--three', help='3rd input option'),
        )
        @option_group(
            'Output options',
            option('--four / --no-four', help='1st output option'),
            option('--five', help='2nd output option'),
            option('--six', help='3rd output option'),
            constraint=RequireAtLeast(1),
        )
        # Options that don't belong to any option group (including --help)
        # are shown under "Other options"
        @option('--seven', help='first uncategorized option',
                type=click.Choice(['yes', 'no', 'ask']))
        @option('--height', help='second uncategorized option')
        def cli(**kwargs):
            """ A CLI that does nothing. """
            print(kwargs)

.. tabbed:: Generated help

    .. code-block:: none

        Usage: clouptest [OPTIONS]

          A CLI that does nothing.

        Input options:
          This is a very long description of the option group. I don't think this is
          needed very often; still, if you want to provide it, you can pass it as
          2nd positional argument or as keyword argument 'help' after all options.
          -o, --one TEXT        1st input option
          --two TEXT            2nd input option
          --three TEXT          3rd input option

        Output options: [at least 1 required]
          --four / --no-four    1st output option
          --five TEXT           2nd output option
          --six TEXT            3rd output option

        Other options:
          --seven [yes|no|ask]  first uncategorized option
          --height TEXT         second uncategorized option
          --help                Show this message and exit.

.. admonition:: The default option group

    Options that are not assigned to any user-defined option group are listed
    under a section which is shows at the bottom. This section is titled
    "Other options", unless the default group is the only one defined, in which
    case ``cloup.Command`` behaves like a normal ``click.Command``, naming it
    just "Options".

In the example above, I used the :func:`cloup.option` decorator to define options
but you can use :func:`click.option` as well. There's no practical difference
between the two when using ``@option_group``.

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
                                       when aligning
          --two TEXT                   This description is more likely to be wrapped
                                       when aligning
          --three TEXT                 This description is more likely to be wrapped
                                       when aligning

        Output options:
          --four                       This description is more likely to be wrapped
                                       when aligning
          --five TEXT                  This description is more likely to be wrapped
                                       when aligning
          --six TEXT                   This description is more likely to be wrapped
                                       when aligning

        Other options:
          --seven [a|b|c|d|e|f|g|h|i]  First uncategorized option
          --height TEXT                Second uncategorized option
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
    :class:`HelpFormatter` parameter ``max_col1_width``, which defaults to 30.


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
        'Input options', help='This is a very useful description of the group')
    output_grp = OptionGroup(
        'Output options', constraint=SetAtLeast(1))

    @cloup.command('clouptest')
    # Input options
    @input_grp.option('-o', '--one', help='1st input option')
    @input_grp.option('--two', help='2nd input option')
    # Output options
    @output_grp.option('--four / --no-four', help='1st output option')
    @output_grp.option('--five', help='2nd output option')
    def cli_flat(**kwargs):
        """ A CLI that does nothing. """
        print(kwargs)

Equivalently, you could pass the option group as an argument to ``cloup.option``:

.. code-block:: python

    @cloup.option('-o', '--one', help='1st input option', group=input_grp)

Note that, in both cases, :class:`OptionGroup` instances work as "markers" for
options, not as containers of options: when you add an option nothing happens
to the corresponding option group.

Option groups without decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For some reason, you may need to work at a lower level, by passing parameters
to a ``Command`` constructor. In that case you can use :class:`GroupedOption`::

    from cloup import Command, GroupedOption, OptionGroup

    output_opts = OptionGroup("Output options")

    params = [
        GroupedOption('--verbose', is_flag=True, group=output_opts),
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
class ``GroupedOption``, this ``group`` attribute is added and set by monkey-patching.

When the command is initialized, ``OptionGroupMixin`` groups all options by
their ``group`` attribute. Options that don't have a ``group`` attribute or have
it set to ``None`` are put into the "default option group" (together with
``--help``).

In order to show option groups in the command help, ``OptionGroupMixin``
"overrides" ``Command.format_options``.


Feature support
---------------

This features depends on two mixins:

- (*required*) :class:`~cloup.OptionGroupMixin`
- (*optional*) :class:`~cloup.ConstraintMixin`, if you want to use constraints.

``cloup.Command`` is the only command class that supports this feature, including
both these mixins.

.. attention::
    ``cloup.Group`` doesn't support option groups nor constraints.
    This is intentional: a ``Group`` should have only a few options, so they
    should not need neither option groups nor constraints. (But I may be wrong;
    if you disagree, open an issue describing your use case). Anyway, you can
    easily subclass ``cloup.Group`` to include the above mixins::

        from cloup import ConstraintMixin, OptionGroupMixin, Group

        class MyGroup(ConstraintMixin, OptionGroupMixin, Group):
            pass
