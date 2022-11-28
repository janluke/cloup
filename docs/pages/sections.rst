.. highlight:: none

Subcommand sections
===================

Cloup allows you to organize the subcommand of a ``Group`` (or, more in general, of
a ``MultiCommand``) in multiple help sections. Each such help section is
represented by a :class:`~cloup.Section` instance, which is just a titled
container for commands.

A ``Section`` can be:

- **sorted** -- it lists the commands in alphabetical order
- **unsorted** -- it lists the commands in the order they are added to the section.

All sections defined by the developer are unsorted by default. You can create a
sorted section by passing ``sorted=True`` or by using the static method
``Section.sorted(*commands)``.

Adding full sections
--------------------

This is my favourite way of structuring my sections.
You can find a runnable example that implements part of the help of Git
`here <https://github.com/janLuke/cloup/blob/master/examples/git_sections.py>`_.
The code below is based on that example.

.. tabbed:: Code
    :new-group:

    .. code-block:: python

        import cloup
        from .commands import (  # import your subcommands
            git_clone, git_init, git_rm, git_sparse_checkout, git_mv,
            git_status, git_log)

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
        # Subcommands that are not assigned to a specific section
        # populate the "default section"
        git.add_command(git_status)
        git.add_command(git_log)


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
          log              Show commit logs
          status           Show the working tree status


All commands that are not explicitly assigned to a section are assigned to a
**default (sorted) section**. This section is titled "Other commands",
unless it is the only section defined, in which case ``cloup.Group`` behaves
like a normal ``click.Group``, naming it just "Commands".

Each call of :class:`Group.section` instantiates a new :class:`~cloup.Section`
and adds it to the ``Group``. Of course, when you add a section, all its
commands added to the ``Group``.

In alternative, you can create a list of ``Section`` objects and pass it as the
``sections`` argument of :func:`cloup.group`:

.. code-block:: python

    import cloup
    from cloup import Section

    # [...] omitting import/definition of subcommands

    SECTIONS = [
        Section('Start a working area (see also: git help tutorial)',
                [git_clone, git_init]),
        Section('Work on the current change (see also: git help everyday)',
                [git_rm, git_sparse_checkout, git_mv])
    ]

    @cloup.group('git', sections=SECTIONS)
    def git():
        return 0


Adding subcommands one at a time
--------------------------------
In Cloup, all ``Group`` methods for adding subcommands, i.e. ``Group.command``,
``Group.group`` and ``Group.add_command``, have an additional ``section``
argument that you can (optionally) use to assign a subcommand to a ``Section``.

.. code-block:: python

    import cloup
    from cloup import Section

    # Define sections without filling them.
    # I'm using a class as a namespace here.
    class Sect:
        START_WORKING_AREA = Section(
            'Start a working area (see also: git help tutorial)')
        WORK_CURRENT_CHANGE = Section(
            'Work on the current change (see also: git help everyday)'

    @cloup.group('git')
    def git():
        return 0

    @git.command('init', section=Sect.START_WORKING_AREA)
    def git_init():
        pass

    @git.command('mv', section=Sect.WORK_CURRENT_CHANGE)
    def git_mv():
        pass

Note that -- differently from ``OptionGroup`` instances -- ``Section`` instances
don't act as simple markers, they act as *containers* from the start: they are
mutated every time you assign a subcommand to them.
