import logging
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import click

import cloup
from cloup import Context

logger = logging.getLogger(__name__)

PathType = Union[str, Path]
CommandType = TypeVar("CommandType", bound=click.Command)


class LazyLoaded(Generic[CommandType]):
    def __init__(
        self,
        name: str,
        short_help: str,
        path: PathType,
        identifier: Optional[str] = None,
        hidden: bool = False,
        deprecated: bool = False,
        aliases: Optional[List[str]] = None,
        **extra,
    ):
        """Proxy for a command defined in a file that is not loaded until it's
        actually needed. The loading happens when the calling code tries to
        access an attribute that it's not defined in this proxy object. In order
        to avoid loading files just to display the help of a group, this class
        requires you to pass ``name`` and ``short_help``. Furthermore, it sets
        all fields listed in the __init__ method signature. If you use other
        extensions, you may need to set extra fields. You can pass any extra
        field you want.

        Tip: set the logging level to "DEBUG" to see when a file is loaded and
        to know which attribute triggered the loading.

        Args:
            name: name of the command.
            short_help: short description of the command.
            path: path to the file containing the command.
            identifier:
                identifier of the command inside the file. Default is ``name``.
            **extra:
                any other command attribute that makes sense to set to avoid
                loading the command just for displaying the help of the parent
                command.
        """
        self.name = name
        self.short_help = short_help
        self.path = Path(path)
        self.identifier = identifier or name
        self.hidden = hidden
        self.deprecated = deprecated
        self.aliases = aliases or []
        self.extra = extra
        self._command: Optional[CommandType] = None

    def get_loaded_command(self, reason: Optional[str] = None) -> CommandType:
        if self._command is None:
            logger.debug(f'Loading {self.path} to access attribute `{reason}`')
            self._command = self._load()
        return self._command

    def _load(self) -> CommandType:
        with open(self.path, encoding="utf8") as f:
            ns: Dict[str, Any] = {}
            code = compile(f.read(), self.path.name, 'exec')
            eval(code, ns, ns)
            assert isinstance(ns[self.identifier], click.Command)
            return ns[self.identifier]

    def __getattr__(self, attr):
        if attr in self.extra:
            return self.extra[attr]
        return getattr(self.get_loaded_command(reason=attr), attr)


class LazyGroup(LazyLoaded[cloup.Group], cloup.Group):  # type: ignore
    pass


class LazyCommand(LazyLoaded[cloup.Command], cloup.Command):  # type: ignore
    pass


@cloup.group(context_settings=Context.settings(show_subcommand_aliases=True))
def main():
    pass


def command_path(rel_path: str) -> Path:
    return Path(__file__, "..", "commands", rel_path).resolve()


main.section(
    "Commands",
    LazyCommand(
        "add", "Add files to the staging area.", command_path("add.py")),
    LazyCommand(
        "commit", "Commit changes to the repository.", command_path("commit.py")),
    LazyCommand(
        "push", "Push changes to a remote repository.", command_path("push.py")),
)

if __name__ == '__main__':
    # Set logging level to DEBUG to see if you want to see when a command is loaded
    # and for accessing which attribute.
    logging.basicConfig(level="DEBUG")

    main("add".split())
