=====
cloup
=====

.. image:: https://img.shields.io/pypi/v/cloup.svg
        :target: https://pypi.python.org/pypi/cloup

.. image:: https://img.shields.io/travis/janLuke/cloup.svg
        :target: https://travis-ci.org/janLuke/cloup

cloup (click + group) extends `pallets/click <https://github.com/pallets/click>`_
to add option groups and the possibility of organizing the subcommands of a
``Group`` in multiple help sections.

Currently, this package only affects how the command help is formatted, it doesn't
allow to specify constraints on option groups. Look at
`click-option-group <https://github.com/click-contrib/click-option-group>`_ if
you want that. Nonetheless, constraints would be a very easy addition and may be
added soon.

.. contents:: **Table of contents**
  :local:

Installation
============
To install the last release::

    pip install cloup

Versioning
----------
cloup uses **semantic versioning**. I'll release v1.0 when I'm
satisfied with API and features but cloup is already usable, just
make sure you specify a compatible version number in your list
of requirements if you decide to use it, e.g.::

    cloup==0.3.*

Patch releases are guaranteed to be backwards compatible even
prior v1.0.

Option groups
=============
You can define option groups in two ways or "styles": I'll call them "nested style" and "flat style".
The full code for the examples shown below can also be found in `<examples/option_groups_example.py>`_.

Nested style (recommended)
--------------------------
In "nested style" you make use of the decorator ``option_group``.
This decorator is "overloaded" with two signatures:

.. code-block:: python

    @option_group(name, *options, help=None)    # help as keyword argument
    @option_group(name, help, *options)         # help as 2nd positional argument

I introduced the 2nd signature because I think it looks and feels nicer when you
have to provide a long help that takes multiple lines; also, it reflects how to
help is actually formatted.

Here's an example:

.. code-block:: python

    import cloup
    from cloup import option_group, option

    @cloup.command('clouptest')
    @option_group('Input options',
        "This is a very long description of the option group. I don't think this is "
        "needed very often; still, if you want to provide it, you can pass it as 2nd "
        "positional argument or as keyword argument 'help' after all options.",
        option('-o', '--one', help='1st input option'),
        option('--two', help='2nd input option'),
        option('--three', help='3rd input option')
    )
    @option_group('Output options',
        option('--four / --no-four', help='1st output option'),
        option('--five', help='2nd output option'),
        option('--six', help='3rd output option'),
        # help='You can also pass the help as keyword argument after the options.'
    )
    @option('--seven', help='first uncategorized option', type=click.Choice('yes no ask'.split()))
    @option('--height', help='second uncategorized option')
    def cli(**kwargs):
        """ A CLI that does nothing. """
        print(kwargs)

The help will be::

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

As you can see, the columns of all option groups are aligned. If you want to
format each option group independently, you can pass ``align_option_groups=False``
to ``@command()``.

Flat style
----------
In "flat style", you first define your option groups and then call the ``option()`` method on them.
**Don't reuse** OptionGroup objects in multiple commands.

.. code-block:: python

    input_grp = OptionGroup('Input options', help='This is a very useful description of the group')
    output_grp = OptionGroup('Output options')

    @cloup.command('clouptest', align_option_groups=True)
    @input_grp.option('-o', '--one', help='1st input option')
    @input_grp.option('--two', help='2nd input option')
    @input_grp.option('--three', help='3rd input option')
    @output_grp.option('--four / --no-four', help='1st output option')
    @output_grp.option('--five', help='2nd output option')
    @output_grp.option('--six', help='3rd output option')
    @option('--seven', help='first uncategorized option', type=click.Choice('yes no ask'.split()))
    @option('--height', help='second uncategorized option')
    def cli_flat(**kwargs):
        """ A CLI that does nothing. """
        print(kwargs)


Subcommand sections
===================
See the full example code `here <examples/git_sections.py>`_.

.. code-block:: python

    # {Definitions of subcommands are omitted}

    @cloup.group('git')
    def git():
        return 0

    """
    git.section() creates a new GroupSection object, adds it to git and returns it.

    In the help, sections are shown in the same order they are added.
    Commands in each sections are shown in the same order they are listed, unless
    you pass the argument "sorted=True".
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

The help will be::

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

In alternative to ``git.section()``, you can use:

- ``@cloup.group('git', sections=[<list of GroupSection objects])``)
- ``git.add_section(section)`` to add an existing ``GroupSection`` object
- ``git.add_command(cmd, name, section, ...)``; the section must NOT contain the command
- ``@git.command(cmd, name, section, ...)``

Individual commands don't know the section they belong to.
Neither ``cloup.Command`` nor ``@cloup.command()`` accept a "section" argument.

Credits
=======

For implementing option groups, I started from the idea of `@chrisjsewell <https://github.com/chrisjsewell>`_
presented in `this comment <https://github.com/pallets/click/issues/373#issuecomment-515293746>`_.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
