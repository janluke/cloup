========
Cloup
========

====================  ==========================================================
**Master branch**     |tests-status| |coverage| |latest-docs|
--------------------  ----------------------------------------------------------
**Latest release**    |pypi-release| |python-versions| |release-docs|
====================  ==========================================================

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

.. |latest-docs| image:: https://readthedocs.org/projects/cloup/badge/?version=latest
    :alt: Documentation Status (master branch)
    :target: https://cloup.readthedocs.io/en/latest/

.. |release-docs| image:: https://readthedocs.org/projects/cloup/badge/?version=stable
    :alt: Documentation Status (latest release)
    :target: https://cloup.readthedocs.io/en/stable/

Cloup (= **Cl**\ick + gr\ **oup**\s) contains a set of
`Click <https://github.com/pallets/click>`_ extensions that enable you to:

- define **option groups** with a clean API;

- define **constraints**, including *conditional constraints*, on any group of
  parameters (e.g. ``mutually_exclusive``, ``RequireAtLeast(1)`` etc.);

- (optionally) show an auto-generated description of defined constraints in the
  command help;

- organize the subcommands of a ``MultiCommand`` in multiple **help sections**.

These features are implemented in three **mixins** following the same pattern of
click-contrib extensions. For ease of use, Cloup also provides:

- its own versions of Click commands, obtained by mixing Click classes with the
  mixins mentioned above;
- its own versions of Click decorators, for creating such commands.

.. if-doc-stop-here

Documentation
=============
Read more in the documentation:

* `latest release <https://cloup.readthedocs.io/en/stable/>`_
* `development version <https://cloup.readthedocs.io/en/latest/>`_.
