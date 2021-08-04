
Installation
============
To install the latest stable release, run::

    pip install cloup

Cloup adheres to `semantic versioning <https://semver.org/>`_.

Depending on Cloup: recommendations
-----------------------------------

1. Pin Cloup version
~~~~~~~~~~~~~~~~~~~~
I probably don't need to explain this, but make sure you pin the version you
are using in your requirements file. Dependency management tools like Poetry
will do this automatically but if you still use ``requirements.txt`` or
``setup.py``, you can do it like following:

.. parsed-literal::

    cloup ~= \ |release|\

Patch releases are guaranteed to be backward-compatible even before v1.0.
At each new release, you can check the :doc:`changelog` to see what's changed.

2. Add Click to your requirements too
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Cloup is not a replacement for Click.

- Cloup reimplements or just re-exports many Click symbols but not *all*. You
  may still need to import click for some stuff.

- Cloup doesn't force you to use a specific version of Click; it only
  specifies a range of supported versions; that's an enough reason to add Click
  to your dependencies: to have control on its version as well.
