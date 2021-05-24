.. |pypi-release| image:: https://img.shields.io/pypi/v/cloup.svg
    :alt: Latest release on PyPI
    :target: https://pypi.org/project/cloup/

.. |tests-status| image:: https://github.com/janLuke/cloup/workflows/Tests/badge.svg
    :alt: Tests status
    :target: https://github.com/janLuke/cloup/actions?query=workflow%3ATests

.. |coverage| image:: https://codecov.io/github/janLuke/cloup/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/janLuke/cloup?branch=master

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/cloup.svg
    :alt: Supported versions
    :target: https://pypi.org/project/cloup

.. |dev-docs| image:: https://readthedocs.org/projects/cloup/badge/?version=latest
    :alt: Documentation Status (master branch)
    :target: https://cloup.readthedocs.io/en/latest/

.. |release-docs| image:: https://readthedocs.org/projects/cloup/badge/?version=stable
    :alt: Documentation Status (latest release)
    :target: https://cloup.readthedocs.io/en/stable/

.. |donate| image:: https://img.shields.io/badge/Donate-PayPal-green.svg
    :alt: Donate with PayPal
    :target: https://www.paypal.com/donate?hosted_button_id=4GTN24HXPMNBJ

========
Overview
========

====================  ==========================================================
**Development**       |tests-status| |coverage| |dev-docs| |donate|
--------------------  ----------------------------------------------------------
**Latest release**    |pypi-release| |python-versions| |release-docs|
====================  ==========================================================

**Cloup** (originally from: **Cl**\ick + option gr\ **oup**\s) extends
`Click <https://github.com/pallets/click>`_ with several features:

- **Option groups** with the ``@option_group`` decorator.

- **Constraints** like ``mutually_exclusive``, ``RequireAtLeast(n)`` etc., which
  can be applied, even *conditionally*, to option groups or to any group of
  parameters (including positional arguments).

- Possibility to organize the subcommands of a ``Group`` in multiple help sections.

- A **themeable HelpFormatter** that:

  - allows you to style several elements of the help page according to a theme
  - switches to a different layout when the terminal width is small for the
    standard 2-column layout, so that the help page is readable in all circumstances
  - has more parameters, which give you more control on the format of the help page.

Besides, Cloup is:

- **type-annotated** and provides additional methods so that you can always be
  assisted by your IDE (e.g. ``Context.settings()`` for creating a
  ``context_settings`` dict leveraging auto-completion)
- **extensively tested** with multiple versions of Python and Click (see
  `Tests <https://github.com/janLuke/cloup/actions>`_)
- **well-documented**.


Basic example
=============

.. code-block:: python

    from cloup import Context, HelpFormatter, HelpTheme, command, option, option_group
    from cloup.constraints import RequireAtLeast, mutually_exclusive

    SETTINGS = Context.settings(
        formatter_settings=HelpFormatter.settings(
            theme=HelpTheme.dark()
        )
    )

    @command(context_settings=SETTINGS, no_args_is_help=True)
    @option_group(
        "Cool options",
        option('--foo', help='This text should describe the option --foo.'),
        option('--bar', help='This text should describe the option --bar.'),
        constraint=mutually_exclusive,
    )
    @option_group(
        "Other cool options",
        "This is the optional description of this option group.",
        option('--pippo', help='This text should describe the option --pippo.'),
        option('--pluto', help='This text should describe the option --pluto.'),
        constraint=RequireAtLeast(1),
    )
    def cmd(**kwargs):
        """This is the command description."""
        pass

    if __name__ == '__main__':
        cmd(prog_name='invoked-command')


.. image:: https://www.dropbox.com/s/ev9lljp2v3ndonu/basic-example.png?raw=1
    :alt: Basic example --help screenshot


Supporting the project
======================
Designing, testing and documenting a library takes a lot of time. The most
concrete way to show your appreciation and to support future development is by
donating. Any amount is appreciated.

|donate|

Apart from that, you can help the project by starring it on GitHub, reporting
issues, proposing improvements and contributing with your code!

.. docs-home-end


Documentation
=============

* `Latest stable release <https://cloup.readthedocs.io/en/stable/>`_
* `Development version <https://cloup.readthedocs.io/en/latest/>`_
