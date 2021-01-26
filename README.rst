========
Cloup
========

====================  ==========================================================
**Master branch**     |travis| |coverage| |latest-docs|
--------------------  ----------------------------------------------------------
**Package**           |pypi-release| |python-versions| |release-docs|
====================  ==========================================================

.. |pypi-release| image:: https://img.shields.io/pypi/v/cloup.svg
    :alt: Latest release on PyPI
    :target: https://pypi.org/project/cloup/

.. |travis| image:: https://img.shields.io/travis/com/janluke/cloup/master?label=tests
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/janLuke/cloup?branch=master

.. |coverage| image:: https://codecov.io/github/janLuke/cloup/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/janLuke/cloup?branch=master

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/cloup.svg
    :alt: Supported versions
    :target: https://pypi.org/project/cloup

.. |latest-docs| image:: https://readthedocs.org/projects/cloup/badge/?version=latest
    :alt: Documentation Status (master branch)
    :target: https://cloup.readthedocs.io/en/latest/

.. |release-docs| image:: https://readthedocs.org/projects/cloup/badge/?version=stable
    :alt: Documentation Status (latest release)
    :target: https://cloup.readthedocs.io/en/stable/

Cloup (= **Cl**\ick + gr\ **oup**\s) adds to
`Click <https://github.com/pallets/click>`_ the following features:

- **option groups** for structuring the help of your commands;

- a subpackage for validating **constraints** on any set of parameters;
  constraints are well-integrated with option groups but decoupled from them,
  meaning they can also be used inside the command callback function for
  validating sets of parameters that don't form an option group;

- organization of the subcommands of a ``MultiCommand`` in multiple
  **help sections**.

These features are implemented in **mixins** following the same pattern of
click-contrib extensions. Cloup redefines click command classes mixing them
with these mixins and provides function decorators for creating such commands.

.. if-doc-stop-here

Documentation
=============
Read more at https://cloup.readthedocs.io/en/stable/usage.html
