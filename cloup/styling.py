import dataclasses as dc
from typing import Callable, Optional

import click

from cloup._util import identity

IStyler = Callable[[str], str]


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


@dc.dataclass(frozen=True)
class HelpTheme:
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
    #: Style of the epilog
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
        return HelpTheme(
            command = command or self.command,
            heading = heading or self.heading,
            description = description or self.description,
            constraint = constraint or self.constraint,
            col1 = col1 or self.col1,
            col2 = col2 or self.col2,
            epilog = epilog or self.epilog
        )

    @staticmethod
    def dark():
        return HelpTheme(
            command=Style(fg='bright_yellow'),
            heading=Style(fg='bright_white'),
            constraint=Style(fg='red'),
            col1=Style(fg='bright_yellow'),
            epilog=Style(fg='bright_white'),
        )
