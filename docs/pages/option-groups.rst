
Option groups
=============

.. highlight:: none

Usage
-----
The recommended way of defining option groups is through the decorator
:func:`cloup.option_group`. This decorator is overloaded with two signatures;
the only difference between the two is how you provide the ``help`` argument:

.. code-block:: python

    # help as keyword argument
    @option_group(name, *options, [help], [constraint])

    # help as 2nd positional argument
    @option_group(name, help, *options, [constraint])

- ``name`` is used as title of the option group help section,
- ``help`` is an optional extended description of the option group, shown below
  the name,
- ``constraint`` is an optional instance of :class:`~cloup.constraints.Constraint`
  (see :doc:`constraints` for more info); a description of the constraint is shown
  between squared brackets in the option group title.

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

        Output options [at least 1 required]:
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

In the example above, I used the :func:`cloup.option` decorator to define
options but this is **entirely optional** as you can use :func:`click.option` as
well. The only difference is that :func:`cloup.option` uses
:class:`~cloup.GroupedOption` as default option class, which is just a
:class:`click.Option` with an additional attribute called ``group``.
Nonetheless, **you don't need** to use ``GroupedOption``, because the attribute
``group`` will be added to any type of ``Option`` via monkey-patching anyway.

By default, the help columns of all option groups are aligned; this is consistent
with how ``argparse`` format option groups and I think it's visually pleasing.
Nonetheless, you can also format each option group independently passing
``align_option_groups=False`` to ``@command()``.

An alternative way (flat style)
-------------------------------
In "flat style", you first define your option groups. Then, you use the
:meth:`~cloup.OptionGroup.option` decorator of :class:`~cloup.OptionGroup`:

.. code-block:: python

    from cloup import OptionGroup
    from cloup.constraints import SetAtLeast

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


Mixin dependencies
------------------
This features depends on:

- (*required*) :class:`~cloup.OptionGroupMixin`
- (*optional*) :class:`~cloup.ConstraintMixin`, if you want to use constraints.

Note that ``cloup.Command`` includes both while ``cloup.Group`` doesn't include
neither of them: groups should have only a few options, so they should not need
neither option groups nor constraints.

How it works
-------------
At "low level", this feature is implemented by setting (eventually by monkey-patching)
a ``group`` attribute in newly added ``Option``'s.
If an option is assigned to an option group, ``option.group`` is set to the
corresponding ``OptionGroup`` instance.

When ``OptionGroupMixin`` is initialized, it just groups options by their
``group`` attribute. Options that don't have a ``group`` attribute or have it
set to ``None`` are collected together and will be part of the "default option
group" (together with ``--help``).

In order to show option groups in the command help,
``OptionGroupMixin`` "overrides" ``Command.format_options``.

.. note::
    In Click, help formatting is hard-coded in ``Command`` itself, which is
    quite inflexible. In future Cloup releases, I could extract help formatting
    to an external (easily swappable) class such as ``HelpGenerator``
    ("``HelpFormatter``" is already taken by Click, with another meaning).
