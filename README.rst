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

Cloup (= **Cl**\ick + gr\ **oup**\s) adds to `Click <https://github.com/pallets/click>`_
the following features:

- **option groups** for ``Command``;

- the possibility to organize the subcommands of a ``Group`` in multiple
  **help sections**.

Cloup implements these features by providing subclasses of ``Command`` and ``Group``,
and by defining a new decorator ``@option_group(name, *options, ...)`` decorator.

Currently, cloup only affects how the command help is formatted, it doesn't
allow to specify constraints on option groups. Group constraints are coming
though.

.. if-doc-stop-here

Documentation
=============
Read more at https://cloup.readthedocs.io/.
