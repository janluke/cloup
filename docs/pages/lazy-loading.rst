Lazy-loading
============

.. versionadded:: 0.14.0

.. warning::
    **This feature is experimental.** Not because I'm not sure it works, rather
    because I'm not sure it's worth anything. In my experience, what really
    slows down Python CLIs is the import time due to big dependencies. It's
    probably unlikely your CLI is so big that loading your commands will make
    a huge difference. Nonetheless, lazy-loading can indirectly reduce the
    number of imported dependencies.


How it works
------------

This feature is implemented by the following classes.
It's important you read the doc of :class:`~cloup.lazy.LazyLoaded` to understand
how it works and what what lazy-loading actually means.

.. autosummary::

    ~cloup.lazy.LazyLoaded
    ~cloup.lazy.LazyCommand
    ~cloup.lazy.LazyGroup

The :mod:`cloup.location` module is also related and contains useful utilities
to specify the location of lazy-loaded command.


Minimal example
---------------

.. code-block:: python

    import cloup
    from cloup.lazy import LazyCommand

    @cloup.group()
    def cli():
        pass

    # Let's say you have a command function called "add_cmd" defined in the
    # module "cli.commands.cmd"
    cli.add_command(
        LazyCommand(
            name="cmd",
            short_help="My cool subcommand",
            location="cli.commands.cmd:cmd_name"
        )
    )

The ``location`` argument can be either:

- a string as in the example above, ``{my.module.name}:{symbol}``
- a :class:`Location` object.

Full example
------------
See: https://github.com/janluke/cloup/tree/master/examples/lazy_loading
