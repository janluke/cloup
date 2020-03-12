=====
cloup
=====

.. image:: https://img.shields.io/pypi/v/cloup.svg
        :target: https://pypi.python.org/pypi/cloup

.. image:: https://img.shields.io/travis/janLuke/cloup.svg
        :target: https://travis-ci.org/janLuke/cloup

.. comment:
    .. image:: https://readthedocs.org/projects/cloup/badge/?version=latest
            :target: https://cloup.readthedocs.io/en/latest/?badge=latest
            :alt: Documentation Status


``cloup`` (``CLick`` + ``grOUP``) extends `pallets/click <https://github.com/pallets/click>`_
to add option groups and the possibility of organizing the subcommands of a ``Group``
in multiple help sections.

Currently, this package only affects how the command help is formatted, it doesn't
allow to specify constraints on option groups. Look at
`click-option-group <https://github.com/click-contrib/click-option-group>`_ if
you want that. Nonetheless, constraints would be a very easy addition and may be
added soon.

* Free software: MIT license

Option groups
-------------
The following code

.. code-block:: python

    import click
    import cloup
    from cloup import option_group, option

    @cloup.command('clouptest')
    @click.argument('arg')
    @option_group(
        'Option group A',
        option('--a1', help='1st option of group A'),
        option('--a2', help='2nd option of group A'),
        option('--a3', help='3rd option of group A'),
        help='This is a useful description of group A')
    @option_group(
        'Option group B',
        option('--b1', help='1st option of group B'),
        option('--b2', help='2nd option of group B'),
        option('--b3', help='3rd option of group B'))
    @option('--opt1', help='an uncategorized option')
    @option('--opt2', help='another uncategorized option')
    def cli(**kwargs):
        """ A CLI that does nothing. """
        print(kwargs)

... will print::

    Usage: clouptest [OPTIONS] [ARG]

      A CLI that does nothing.

    Option group A:
      This is a useful description of group A
      --a1 TEXT  1st option of group A
      --a2 TEXT  2nd option of group A
      --a3 TEXT  3rd option of group A

    Option group B:
      --b1 TEXT  1st option of group B
      --b2 TEXT  2nd option of group B
      --b3 TEXT  3rd option of group B

    Other options:
      --opt1 TEXT  an uncategorized option
      --opt2 TEXT  another uncategorized option
      --help       Show this message and exit.


``cloup.Group`` sections
------------------------
See the full example code `here <examples/git_sections.py>`_.

.. code-block:: python

    # {Definitions of subcommands are omitted}

    """
    If "align_sections_help=True" (default), the help column of all sections will
    be aligned; otherwise, each section will be formatted independently.
    """
    @cloup.group('git', align_sections_help=True)
    def git():
        return 0

    """
    git.section() creates a new GroupSection object, adds it to git and returns it.

    In the help, sections are shown in the same order they are added.
    Commands in each sections are shown in the same order they are listed, unless
    you pass the argument "sorted_=True".
    """
    git.section('Start a working area (see also: git help tutorial)', [
        git_clone,
        git_init,
    ])
    git.section('Work on the current change (see also: git help everyday)', [
        git_rm,
        git_sparse_checkout,
        git_mv,
    ])

    # The following commands will be added to the "default section" (a sorted GroupSection)
    git.add_command(cloup.command('fake-2', help='Fake command #2')(f))
    git.add_command(cloup.command('fake-1', help='Fake command #1')(f))

With ``align_sections_help=True``, the help will be::

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


With ``align_sections_help=False``, the help will be::

    Usage: git_sections.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Start a working area (see also: git help tutorial):
      clone  Clone a repository into a new directory
      init   Create an empty Git repository or reinitialize an existing one

    Work on the current change (see also: git help everyday):
      rm               Remove files from the working tree and from the index
      sparse-checkout  Initialize and modify the sparse-checkout
      mv               Move or rename a file, a directory, or a symlink

    Other commands:
      fake-1  Fake command #1
      fake-2  Fake command #2

In alternative to ``git.section()``, you could also use:

- ``@cloup.group('git', sections=[<list of GroupSection objects])``)
- ``git.add_section(section)`` to add an existing ``GroupSection`` object
- ``git.add_command(cmd, name, section, ...)``; the section must NOT contain the command
- ``@git.command(cmd, name, section, ...)``

Individual commands don't know the section they belong to. As a consequence,
neither ``cloup.Command`` nor ``@cloup.command()`` accept a "section" argument.

Credits
-------

For implementing option groups, I started from the idea of `@chrisjsewell <https://github.com/chrisjsewell>`_
presented in `this comment <https://github.com/pallets/click/issues/373#issuecomment-515293746>`_.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
