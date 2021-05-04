import dataclasses as dc
from typing import Callable, NamedTuple, Optional

import click

from cloup._util import identity

#: A callable that takes a string and returns a styled version of it.
IStyler = Callable[[str], str]


class HelpTheme(NamedTuple):
    """Stylesheet for various elements of the help page.

    **Implementation note:** this should have been a frozen ``dataclass``
    but I had to use ``NamedTuple`` instead to work around a MyPy issue:
    https://github.com/python/mypy/issues/5485. Don't rely on this class being
    a ``NamedTuple`` because this will probably change in the future.
    """
    #: Style of the command name.
    command: IStyler = identity

    #: Style of help section headings.
    heading: IStyler = identity

    #: Style of an option group constraint description.
    constraint: IStyler = identity

    #: Style of a help section descriptions.
    description: IStyler = identity

    #: Style of the first column of a definition list.
    col1: IStyler = identity

    #: Style of the second column of a definition list.
    col2: IStyler = identity

    #: Style of the epilog.
    epilog: IStyler = identity

    def with_(
        self, command: Optional[IStyler] = None,
        heading: Optional[IStyler] = None,
        description: Optional[IStyler] = None,
        constraint: Optional[IStyler] = None,
        col1: Optional[IStyler] = None,
        col2: Optional[IStyler] = None,
        epilog: Optional[IStyler] = None,
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
    fg: Optional[str] = None
    bg: Optional[str] = None
    bold: bool = False
    dim: bool = False
    underline: bool = False
    blink: bool = False
    reverse: bool = False
    text_transform: Optional[IStyler] = None
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
