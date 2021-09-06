:tocdepth: 2

.. meta::
    :description lang=en:
        Cloup is a library that extends the Click Python library with several features:
        option groups, constraints for group of parameters, the possibility
        to group the subcommands of a Group in multiple help sections and a
        custom help formatter with support for styling / theming.
    :keywords:
        python, cloup, click, option groups, help sections, constraints,
        mutually exclusive, help colors, help styling, help theming
    :google-site-verification: r5SEmg2wwCURBwKSrL_zQJEJbCVsScFhryur7zdFM3s

.. include:: ../README.rst
    :start-after: docs-index-start
    :end-before: docs-index-code-start

.. testsetup::

    __name__ = "__main__"

.. testcode::

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

    if __name__ == "__main__":
        cmd(["--help"], prog_name='invoked-command', standalone_mode=False)

.. testoutput::
    :hide:
    :options: -ELLIPSIS, +NORMALIZE_WHITESPACE

    Usage: invoked-command [OPTIONS]

    This is the command description.

    Cool options: [mutually exclusive]
    --foo TEXT    This text should describe the option --foo.
    --bar TEXT    This text should describe the option --bar.

    Other cool options: [at least 1 required]
    This is the optional description of this option group.
    --pippo TEXT  This text should describe the option --pippo.
    --pluto TEXT  This text should describe the option --pluto.

    Other options:
        --help        Show this message and exit.

.. include:: ../README.rst
    :start-after: docs-index-code-end
    :end-before: docs-index-end

User guide
==========
Please, note that Cloup documentation doesn't replace
`Click documentation <https://click.palletsprojects.com/en/8.0.x/>`_.

.. toctree::
    :caption: User guide
    :maxdepth: 2

    pages/installation
    pages/option-groups
    pages/constraints
    pages/aliases
    pages/sections
    pages/formatting


.. toctree::
    :caption: API reference
    :hidden:

    autoapi/cloup/index


.. toctree::
    :caption: Project
    :maxdepth: 2
    :hidden:

    GitHub Repository <https://github.com/janluke/cloup>
    Donate <https://www.paypal.com/donate?hosted_button_id=4GTN24HXPMNBJ>
    pages/contributing
    pages/credits
    pages/changelog
