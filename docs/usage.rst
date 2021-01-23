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
    Just make sure you pin the version you are using in your requirements, e.g.::

        cloup==0.5.*

    At each new release, I'll do my best to document what has changed in the
    :doc:`changelog`.

Option groups
=============
This feature is implemented by the :class:`~cloup.OptionGroupMixin` class,
which :class:`cloup.Command` inherits from.

You can define option groups in two ways or "styles". I'll call them

- nested style (recommended),
- flat style.

If you're an adept of the well-known Pythonic principle (*"there should be one
way to do it"*), just use the first and ignore the second.

Two runnable examples can be found in the
`examples folder <https://github.com/janLuke/cloup/tree/master/examples>`_
of the repository.

Nested style
------------
In "nested style" you make use of the decorator :func:`cloup.option_group`.
This decorator is overloaded with two signatures:

.. code-block:: python

    @option_group(name, *options, help=None)  # help as keyword argument
    @option_group(name, help, *options)       # help as 2nd positional argument

The ``name`` is also the title of the corresponding help section. The ``help``
is an optional additional description of the option group.

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
        # The following will be under "Other options" with --help
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

.. admonition:: The default option group

    Options that are not assigned to any user-defined option group are listed
    under a section titled "Other options" which is shows at the bottom.

In the example above, I used the :func:`cloup.option` decorator to define
options but this is entirely optional as you can use :func:`click.option` as
well. The only difference is that :func:`cloup.option` adds a
:class:`cloup.GroupedOption`, which is nothing more than a
:class:`click.Option` with an additional attribute called ``group``.
This attribute will be added anyway.

By default, the columns of all option groups are aligned; I find this visually
pleasing. Nonetheless, you can also format each option group independently
passing ``align_option_groups=False`` to ``@command()``.

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


Subcommand sections
====================
This feature is implemented mostly by the :class:`~cloup.SectionMixin` class,
which :class:`cloup.Group` inherits from.

Each help section is represented by a :class:`~cloup.Section` instance, which
is just a container for commands with a ``title``. A ``Section`` can be:

- *sorted* -- it lists the commands in alphabetical order
- *unsorted* (default) -- it lists the commands in the order they are added to
  the section.

You can create a sorted section by passing ``sorted=True`` or by using the
static method ``Section.sorted()``.

.. admonition:: The default section

    The commands that are not explicitly assigned to a section are assigned to a
    "default section", which is sorted.

You can find a runnable example that implements part of the help of Git
`here <https://github.com/janLuke/cloup/blob/master/examples/git_sections.py>`_.

Adding full sections
--------------------
My favorite way of defining sections is doing it all in one place below the
``Group`` itself, as following:

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        import cloup
        from .commands import ( # import your subcommands implemented elsewhere
            git_init, git_clone, git_rm, git_sparse_checkout, git_mv)

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

        # The following commands will be added to the "default section" (a sorted Section)
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

Each call of ``section()`` creates a new ``Section`` instance and adds it to
the ``Group``. When you add a section, all the contained subcommands are of
course added to the ``Group`` (as if you called ``add_command`` for each of
them).

In alternative, you can create a list of ``Section`` objects and pass it as the
``sections`` argument of :func:`cloup.group`:

.. code-block:: python

    import cloup
    from cloup import Section
    # import subcommands git_init, git_clone ecc...

    SECTIONS = [
        Section('Start a working area (see also: git help tutorial)',
                git_clone, git_init),
        Section('Work on the current change (see also: git help everyday)',
                git_rm, git_sparse_checkout, git_mv)
    ]

    @cloup.group('git', sections=SECTIONS)
    def git():
        return 0

Adding subcommands
------------------
If you prefer, you can also assign a subcommand to a section when you add
a new one using the decorators ``@group.command`` and ``@group.group`` or
``group.add_command``; in Cloup, all these methods have indeed an additional
(optional) argument ``section``.

.. code-block:: python

    import cloup
    from cloup import Section

    # Define sections without filling them in one place
    class GitSection:
        START_WORKING_AREA = Section(
            'Start a working area (see also: git help tutorial)')
        WORK_CURRENT_CHANGE = Section(
            'Work on the current change (see also: git help everyday)'

    @cloup.group('git')
    def git():
        return 0

    # Assign each subcommand to a section
    @git.command('init', section=GitSection.START_WORKING_AREA)
    def git_init():
        pass

    @git.command('mv', section=GitSection.WORK_CURRENT_CHANGE)
    def git_mv():
        pass
