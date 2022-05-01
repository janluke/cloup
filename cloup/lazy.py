import importlib
import logging
from typing import Generic, List, Optional, TypeVar, Union

import click

import cloup
from cloup.location import Location, as_location

logger = logging.getLogger(__name__)

CommandType = TypeVar("CommandType", bound=click.Command)


class LazyLoaded(Generic[CommandType]):
    """
    Proxy for a command defined in a file that is not loaded until it's
    actually needed.

    The loading happens when the calling code tries to access an attribute
    that it's not defined in this proxy object. In order to avoid loading
    files just to display the ``--help`` of a group, this class requires
    you to pass ``name`` and ``short_help`` and sets various attributes
    (see ``__init__`` signature) that are used when generating the help text.

    If you use other extensions, you may need to set extra fields. Any extra
    argument you pass to ``__init__`` will set a corresponding field.

    Tip: set the logging level to "DEBUG" to see when a file is loaded and
    to know which attribute triggered the loading.
    """

    def __init__(
        self,
        name: str,
        short_help: str,
        location: Union[str, Location],
        hidden: bool = False,
        deprecated: bool = False,
        aliases: Optional[List[str]] = None,
        **extra,
    ):
        """
        :param name: name of the command.
        :param short_help: short description of the command.
        :param location:
            command location; this can be an instance of :class:`~cloup.location.Location`
            or a string ``{module}:{symbol}`` where ``module`` is the module
            containing the command and ``symbol`` is the name of the command
            function/object.
        :param identifier:
            identifier of the command inside the file. Default is ``name``.
        :param **extra:
            any other command attribute that makes sense to set to avoid
            loading the command just for displaying the help of the parent
            command.
        """
        self.name = name
        self.short_help = short_help
        self.location = as_location(location)
        self.hidden = hidden
        self.deprecated = deprecated
        self.aliases = aliases or []
        self.extra = extra
        self._command: Optional[CommandType] = None

    def get_loaded_command(self, reason: Optional[str] = None) -> CommandType:
        if self._command is None:
            logger.debug(f'Loading {self.location} to access attribute `{reason}`')
            self._command = self._load()
        return self._command

    def _load(self) -> CommandType:
        module_name, symbol = self.location
        module = importlib.import_module(module_name)
        cmd = getattr(module, symbol)
        assert isinstance(cmd, click.Command)
        return cmd

    def __getattr__(self, attr):
        if attr in self.extra:
            return self.extra[attr]
        return getattr(self.get_loaded_command(reason=attr), attr)


class LazyGroup(LazyLoaded[cloup.Group], cloup.Group):  # type: ignore
    """Lazy-loaded :class:`cloup.Group`. See :class:`LazyLoaded` for more.

    .. versionadded:: 0.14.0
    """
    pass


class LazyCommand(LazyLoaded[cloup.Command], cloup.Command):  # type: ignore
    """Lazy-loaded :class:`cloup.Command`. See :class:`LazyLoaded` for more.

    .. versionadded:: 0.14.0
    """
    pass
