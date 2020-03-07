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


Adds option groups to `pallets/click <https://github.com/pallets/click>`_.

This package only affects how the command help is formatted, it doesn't
(and never will) allow to specify constraints on option groups. Look at
`click-option-group <https://github.com/click-contrib/click-option-group>`_ if
you want that.

* Free software: MIT license

Example
-------
The following code

.. code-block:: python

    import click
    import cloup
    from cloup import option_group, option

    @cloup.command('clouptest')
    @click.argument('arg')
    @option_group('Option group A', [
        option('--a1', help='1st option of group A'),
        option('--a2', help='2nd option of group A'),
        option('--a3', help='3rd option of group A')],
        help='This is a useful description of group A',
    )
    @option_group('Option group B', [
        option('--b1', help='1st option of group B'),
        option('--b2', help='2nd option of group B'),
        option('--b3', help='3rd option of group B'),
    ])
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

Credits
-------

I started from the code written by `@chrisjsewell <https://github.com/chrisjsewell>`_
in `this comment <https://github.com/pallets/click/issues/373#issuecomment-515293746>`_.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
