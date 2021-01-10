============
Usage
============

.. Setting this to "python" would be more useful but, because of bug in the
.. PyCharm rst plugin, I don't get Python syntax highlighting in the IDE.
.. highlight:: none

Installation
============
To install the **latest release**, run::

    pip install cloup

Cloup adheres to `semantic versioning <https://semver.org/>`_.

.. attention::
    Since Cloup has not reached v1.0, its API is not to be considered stable.
    This doesn't mean you can't already use it: it is already tested and usable.
    Just make sure you specify a version constraint in your list of
    requirements, e.g.::

        cloup==0.3.*

Option groups
=============
You can define option groups in two ways or "styles". I'll call them

- nested style,
- flat style.

The full code for the examples shown below can also be found in the
`examples folder <https://github.com/janLuke/cloup/tree/master/examples>`_ on GitHub.

Nested style (recommended)
--------------------------
In "nested style" you make use of the decorator :func:`cloup.option_group`.
This decorator is overloaded with two signatures

.. code-block:: python

    @option_group(name, *options, help=None)  # help as keyword argument
    @option_group(name, help, *options)       # help as 2nd positional argument

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        import cloup
        from cloup import option_group, option

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
        )
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

        Output options:
          --four / --no-four    1st output option
          --five TEXT           2nd output option
          --six TEXT            3rd output option

        Other options:
          --seven [yes|no|ask]  first uncategorized option
          --height TEXT         second uncategorized option
          --help                Show this message and exit.

.. note::
    Options that are not assigned to any user-defined option group are listed
    under a section titled "Other options" which is shows at the bottom.

In the example above, I used the :func:`cloup.option` decorator to define
options but this is entirely optional as you can use :func:`click.option` as
well. The only difference is that :func:`cloup.option` adds a
:class:`cloup.GroupedOption`, which is nothing more than a
:class:`click.Option` with an additional attribute called ``group``.

By default, the columns of all option groups are aligned. Most people find
this visually pleasing. Nonetheless, you can also format each option group
independently passing ``align_option_groups=False`` to ``@command()``.

Flat style
----------
In "flat style", you first define your option groups. Then, you use the
:meth:`~cloup.OptionGroup.option` decorator of :class:`~cloup.OptionGroup`:

.. code-block:: python

    from cloup import OptionGroup

    some_group = OptionGroup(
        'Input options', help='This is a very useful description of the group')
    another_group = OptionGroup('Output options')

    @cloup.command('clouptest', align_option_groups=True)
    @some_group.option('-o', '--one', help='1st input option')
    @some_group.option('--two', help='2nd input option')
    @another_group.option('--four / --no-four', help='1st output option')
    @another_group.option('--five', help='2nd output option')
    def cli_flat(**kwargs):
        """ A CLI that does nothing. """
        print(kwargs)


Grouping subcommands
====================
You can use :class:`cloup.Group` when you want to organize the subcommands of a
``Group`` in multiple help sections. The api is trivial and the formatting is
similar to that of options groups. You can find the full example code
`here <https://github.com/janLuke/cloup/blob/master/examples/git_sections.py>`_.

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        # import subcommands git_init, git_clone ecc...

        @cloup.group('git')
        def git():
            return 0

        git.section(
            'Start a working area (see also: git help tutorial)',
            git_clone,
            git_init
        )
        git.section(
            'Work on the current change (see also: git help everyday)',
            git_rm,
            git_sparse_checkout,
            git_mv
        )

        # The following commands will be added to the "default section" (a sorted GroupSection)
        git.add_command(cloup.command('fake-2', help='Fake command #2')(f))
        git.add_command(cloup.command('fake-1', help='Fake command #1')(f))


.. tabbed:: Generated help

    .. code-block:: none

        Usage: git [OPTIONS] COMMAND [ARGS]...

        Options:
          --help  Show this message and exit.

        Start a working area (see also: git help tutorial):
          clone            Clone a repository into a new directory
          init             Create an empty Git repository or reinitialize an...

        Work on the current change (see also: git help everyday):
          rm               Remove files from the working tree and from the index
          sparse-checkout  Initialize and modify the sparse-checkout
          mv               Move or rename a file, a directory, or a symlink

        Other commands:
          fake-1           Fake command #1
          fake-2           Fake command #2

.. note::
    - Sections are shown in the same order they are added to the group.
    - By default, the commands of a user-defined section are shown in the same
      order they are listed. Passing ``sorted=True``, you can create a sorted
      section, i.e. a section where commands are sorted by name.
    - The default section (titled "Other commands") is a sorted section.

In alternative, you can create a list of :class:`~cloup.GroupSection` yourself
and pass it as the ``sections`` argument of :func:`cloup.group`:

.. code-block:: python

    # import subcommands git_init, git_clone ecc...

    SECTIONS = [
        GroupSection('Start a working area (see also: git help tutorial)',
                     git_clone, git_init),
        GroupSection('Work on the current change (see also: git help everyday)',
                     git_rm, git_sparse_checkout, git_mv)
    ]

    @cloup.group('git', sections=SECTIONS)
    def git():
        return 0

.. tip::
    Instead of passing ``sorted=True`` to the constructor, you can create a
    sorted section by using the static method ``GroupSection.sorted(...)``.
