import dataclasses as dc
from typing import Callable, NamedTuple, Optional

import click

from cloup._util import FrozenSpace, click_version_tuple, identity, pop_many

IStyle = Callable[[str], str]
"""A callable that takes a string and returns a styled version of it."""


class HelpTheme(NamedTuple):
    """A collection of styles for several elements of the help page.

    A "style" is just a function or a callable that takes a string and returns
    a styled version of it. This means you can use your favorite styling/color
    library (like rich, colorful etc). Nonetheless, given that Click has some
    basic styling functionality built-in, Cloup provides the :class:`Style`
    class, which is a wrapper of the ``click.style`` function.

    *Implementation note:* this should have been a frozen ``dataclass``
    but I had to use ``NamedTuple`` instead to work around a MyPy issue
    (https://github.com/python/mypy/issues/5485).
    """
    #: Style of the invoked command name (in Usage).
    invoked_command: IStyle = identity

    #: Style of the invoked command description (below "Usage").
    command_help: IStyle = identity

    #: Style of help section headings.
    heading: IStyle = identity

    #: Style of an option group constraint description.
    constraint: IStyle = identity

    #: Style of the help text of a section (the optional paragraph below the heading).
    section_help: IStyle = identity

    #: Style of the first column of a definition list (options and command names).
    col1: IStyle = identity

    #: Style of the second column of a definition list (help text).
    col2: IStyle = identity

    #: Style of the epilog.
    epilog: IStyle = identity

    def with_(
        self, invoked_command: Optional[IStyle] = None,
        command_help: Optional[IStyle] = None,
        heading: Optional[IStyle] = None,
        constraint: Optional[IStyle] = None,
        section_help: Optional[IStyle] = None,
        col1: Optional[IStyle] = None,
        col2: Optional[IStyle] = None,
        epilog: Optional[IStyle] = None,
    ) -> 'HelpTheme':
        kwargs = {key: val for key, val in locals().items() if val is not None}
        kwargs.pop('self')
        if kwargs:
            return self._replace(**kwargs)
        return self

    @staticmethod
    def dark():
        return HelpTheme(
            invoked_command=Style(fg='bright_yellow'),
            heading=Style(fg='bright_white'),
            constraint=Style(fg='red'),
            col1=Style(fg='bright_yellow'),
            epilog=Style(fg='bright_white'),
        )

    @staticmethod
    def light():
        return HelpTheme(
            invoked_command=Style(fg='yellow'),
            heading=Style(fg='bright_blue'),
            constraint=Style(fg='red'),
            col1=Style(fg='yellow'),
            epilog=Style(fg='bright_black'),
        )


@dc.dataclass(frozen=True)
class Style:
    """Wraps func:`click.style` for a better integration with :class:`HelpTheme`.

    Available colors are defined as static constants in :class:`click.styling.Color`.

    Arguments are set to ``None`` by default. Passing ``False`` to boolean args
    or ``Color.reset`` as color causes a reset code to be inserted.

    This class is conceptually to a partial application of :func:`click.style`
    (see :func:`functools.partial` if you don't know what "partial" means).
    This class has one argument less (``reset``, which is always ``True``)
    and an argument more (``text_transform``).

    See func:`click.style` for more info.

    .. warning::
        The arguments ``overline``, ``italic`` and ``strikethrough`` are only
        supported in Click 8 and will be ignored if you are using Click 7.

    .. versionadded:: 0.8.0
    """
    fg: Optional[str] = None
    bg: Optional[str] = None
    bold: Optional[bool] = None
    dim: Optional[bool] = None
    underline: Optional[bool] = None
    overline: Optional[bool] = None
    italic: Optional[bool] = None
    blink: Optional[bool] = None
    reverse: Optional[bool] = None
    strikethrough: Optional[bool] = None
    #: A generic text transformation; use it to pass function like ``str.upper``.
    text_transform: Optional[IStyle] = None
    _style_kwargs: Optional[dict] = dc.field(init=False, default=None)

    def __call__(self, text: str) -> str:
        if self._style_kwargs is None:
            kwargs = pop_many(dc.asdict(self), 'text_transform', '_style_kwargs')
            if int(click_version_tuple[0]) < 8:
                # These arguments are not supported in Click < 8. Ignore them.
                pop_many(kwargs, 'overline', 'italic', 'strikethrough')
            object.__setattr__(self, '_style_kwargs', kwargs)
        else:
            kwargs = self._style_kwargs

        if self.text_transform:
            text = self.text_transform(text)
        return click.style(text, **kwargs)


class Color(FrozenSpace):
    black = "black"
    red = "red"
    green = "green"
    yellow = "yellow"
    blue = "blue"
    magenta = "magenta"
    cyan = "cyan"
    white = "white"
    reset = "reset"
    bright_black = "bright_black"
    bright_red = "bright_red"
    bright_green = "bright_green"
    bright_yellow = "bright_yellow"
    bright_blue = "bright_blue"
    bright_magenta = "bright_magenta"
    bright_cyan = "bright_cyan"
    bright_white = "bright_white"
