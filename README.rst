.. raw:: html

    <p align="center">
        <img
            src="https://raw.githubusercontent.com/janLuke/cloup/master/docs/_static/logo-on-white.svg"
            width="50%" />
    </p>

    <p align="center">
        <i>
            <a href="https://github.com/pallets/click">Click</a>
            + option groups + constraints + themes + ...
        </i>
    </p>

    <p align="center">
        <a href="https://cloup.readthedocs.io/">https://cloup.readthedocs.io/</a>
    </a>

----------

.. docs-index-start

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
|pypi-release| |python-versions| |tests-status| |coverage| |dev-docs| |donate|

**Cloup** — originally from "**Cl**\ick + option gr\ **oup**\s" — enriches
`Click <https://github.com/pallets/click>`_ with several features that make it
more expressive and configurable:

- **option groups**

- **constraints**, like ``mutually_exclusive``, that can be applied to any group
  of parameters, even *conditionally*

- **sections for subcommands**, i.e. the possibility to organize the subcommands of a
  ``Group`` in multiple help sections

- a **themeable HelpFormatter**  that:

  - has more parameters for adjusting widths and spacing, which can be provided
    at the context and command level
  - use a different layout when the terminal width is small, to improve readability.

Moreover, Cloup improves on **IDE support** providing *detailed* type hints for
Click decorators and adding the static methods ``Context.settings()`` and
``HelpFormatter.settings()`` for creating settings dictionaries.

Cloup is extensively **tested and documented.** Tests are run against multiple
versions of Python (>=3.6) and Click (>=7.2).


A simple example
================

.. code-block:: python

    from cloup import (
        HelpFormatter, HelpTheme, Style,
        command, option, option_group
    )
    from cloup.constraints import RequireAtLeast, mutually_exclusive

    # Check the docs for all available arguments of HelpFormatter and HelpTheme.
    formatter_settings = HelpFormatter.settings(
        theme=HelpTheme(
            invoked_command=Style(fg='bright_yellow'),
            heading=Style(fg='bright_white', bold=True),
            constraint=Style(fg='magenta'),
            col1=Style(fg='bright_yellow'),
        )
    )

    # In a multi-command app, you can pass formatter_settings as part
    # of your context_settings so that they are propagated to subcommands.
    @command(formatter_settings=formatter_settings)
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


.. image:: https://raw.githubusercontent.com/janLuke/cloup/master/docs/_static/basic-example.png
    :alt: Basic example --help screenshot

If you don't provide ``--pippo`` or ``--pluto``:

.. code-block:: text

    Usage: invoked-command [OPTIONS]
    Try 'invoked-command --help' for help.

    Error: at least 1 of the following parameters must be set:
      --pippo
      --pluto


Supporting the project
======================
Designing, testing and documenting a library takes a lot of time. The most
concrete way to show your appreciation and to support future development is by
donating. Any amount is appreciated.

|donate|

Apart from that, you can help the project by starring it on GitHub, reporting
issues, proposing improvements and contributing with your code!

.. docs-index-end


Links
=====

* Documentation (release_ | development_)
* `Changelog <https://cloup.readthedocs.io/en/stable/pages/changelog.html>`_
* `GitHub repository <https://github.com/janLuke/cloup>`_
* `Q&A and discussions <https://github.com/janLuke/cloup/discussions>`_

.. _release: https://cloup.readthedocs.io/en/stable/#user-guide
.. _development: https://cloup.readthedocs.io/en/latest/#user-guide
