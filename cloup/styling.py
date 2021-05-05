import dataclasses as dc
from typing import Callable, NamedTuple, Optional

import click

from cloup._util import identity

#: A callable that takes a string and returns a styled version of it.
IStyle = Callable[[str], str]


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
    #: Style of the command name.
    command: IStyle = identity

    #: Style of help section headings.
    heading: IStyle = identity

    #: Style of an option group constraint description.
    constraint: IStyle = identity

    #: Style of a help section descriptions.
    description: IStyle = identity

    #: Style of the first column of a definition list.
    col1: IStyle = identity

    #: Style of the second column of a definition list.
    col2: IStyle = identity

    #: Style of the epilog.
    epilog: IStyle = identity

    def with_(
        self, command: Optional[IStyle] = None,
        heading: Optional[IStyle] = None,
        description: Optional[IStyle] = None,
        constraint: Optional[IStyle] = None,
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
            command=Style(fg='bright_yellow'),
            heading=Style(fg='bright_white'),
            constraint=Style(fg='red'),
            col1=Style(fg='bright_yellow'),
            epilog=Style(fg='bright_white'),
        )

    @staticmethod
    def light():
        return HelpTheme(
            command=Style(fg='yellow'),
            heading=Style(fg='bright_blue'),
            constraint=Style(fg='red'),
            col1=Style(fg='yellow'),
            epilog=Style(fg='bright_black'),
        )


@dc.dataclass(frozen=True)
class Style:
    """Wraps ``click.style`` for a better integration with :class:`HelpTheme`.
    This is conceptually equivalent to ``functools.partial(click.style, **kwargs)``.
    The difference is in the improved developer experience: with this class,
    you get auto-complete, typing and a shorter alias. This class also doesn't
    include arguments of ``click-style`` that are useless in this context, and
    add the argument ``text_transform``.
    """
    fg: Optional[str] = None
    bg: Optional[str] = None
    bold: bool = False
    dim: bool = False
    underline: bool = False
    blink: bool = False
    reverse: bool = False
    #: A generic text transformation; use it to pass function like ``str.upper``.
    text_transform: Optional[IStyle] = None
    _click_kwargs: dict = dc.field(init=False, default_factory=dict)

    def __post_init__(self):
        click_kwargs = dc.asdict(self)
        click_kwargs.pop('text_transform')
        click_kwargs.pop('_click_kwargs')
        object.__setattr__(self, '_click_kwargs', {
            key: (None if not value else value)
            for key, value in click_kwargs.items()
        })

    def __call__(self, text: str) -> str:
        if self.text_transform:
            text = self.text_transform(text)
        return click.style(text, **self._click_kwargs)
