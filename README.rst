========
Cloup
========

====================  ==========================================================
**Tests**             |travis| |coverage|
--------------------  ----------------------------------------------------------
**Package**           |version| |supported-pythons|
====================  ==========================================================

.. |version| image:: https://img.shields.io/pypi/v/cloup.svg
    :alt: PyPI Package
    :target: https://pypi.org/project/cloup/

.. |travis| image:: https://img.shields.io/travis/janLuke/cloup.svg
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/janLuke/cloup?branch=master

.. |coverage| image:: https://codecov.io/github/janLuke/cloup/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/janLuke/cloup?branch=master

.. |supported-pythons| image:: https://img.shields.io/pypi/pyversions/cloup.svg
    :alt: Supported versions
    :target: https://pypi.org/project/cloup

Cloup (= **Cl**\ick + gr\ **oup**\s) adds to `Click <https://github.com/pallets/click>`_
the following features:

- **option groups** for ``Command``;

- the possibility to organize the subcommands of a ``Group`` in multiple
  **subcommand help sections**.

Cloup implements these features by providing subclasses of ``Command`` and ``Group``,
and by defining a new decorator ``@option_group(name, *options, ...)`` decorator.

Currently, cloup only affects how the command help is formatted, it doesn't
allow to specify constraints on option groups. Group constraints are coming
though.

.. if-doc-stop-here

Documentation
=============
Read more at https://cloup.readthedocs.io/.
