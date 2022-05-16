Subcommand aliases
==================

Aliases are alternative names for subcommands. They are often used to
define "shortcuts", e.g. ``i`` for ``install``.

Usage
-----
The usage of this feature is pretty straightforward: just use the ``aliases``
parameter exposed by Cloup command decorators.

.. code-block:: python
    :emphasize-lines: 6,13

    @cloup.group(show_subcommand_aliases=True)
    def cli():
        """A package installer."""
        pass

    @cli.command(aliases=['i', 'add'])
    @cloup.argument('pkg')
    def install(pkg: str):
        """Install a package."""
        print('install', pkg)

    # Aliases works even if cls is not a Cloup command class
    @cli.command(aliases=['uni', 'rm'], cls=click.Command)
    @cloup.argument('pkg')
    def uninstall(pkg: str):
        """Uninstall a package."""
        print('uninstall', pkg)

.. note::
    It's worth noting that the ``aliases`` argument is exposed  by *all* command
    decorators, not just ``Group.command`` and ``Group.group`` (used in the
    example above). This is possible because aliases are stored in the subcommand,
    so a ``Group`` can get them from the added command itself.

.. _show-subcommand-aliases:

Help output of the group
------------------------

By default, aliases are **not** shown in the "Commands" section(s) of the ``Group``.
If you want to show them, you can set ``show_subcommand_aliases=True`` as in the
example above. This argument is also available as a context setting.
With ``show_subcommand_aliases=True`` the ``--help`` output is:

.. code-block:: none
    :emphasize-lines: 9-10

    Usage: cli [OPTIONS] COMMAND [ARGS]...

      A package installer.

    Options:
      --help  Show this message and exit.

    Commands:
      install (i, add)     Install a package.
      uninstall (uni, rm)  Uninstall a package.

.. admonition:: Customizing the format of the first column
    :class: note

    If you ever feel the need, you can easily customize the format of the first
    column overriding the method :meth:`Group.format_subcommand_name`.
    My suggestion is to copy the default implementation and modify it.


Help output of the subcommand
-----------------------------

.. attention::
    Aliases are shown **only** in the ``--help`` output of subcommands that
    extends ``cloup.Command``. So, normal ``click.Command`` won't do it.

.. code-block:: text
    :emphasize-lines: 2

    Usage: cli install [OPTIONS] PKG
    Aliases: i, add

      Install a package.

    Options:
      --help  Show this message and exit.

This is possible because aliases are stored in the subcommand itself, precisely
in the ``aliases`` attribute. Cloup commands declare this attribute and accept
it as a parameter. For all other type of commands, Cloup uses monkey-patching
to add this attribute.

