from pathlib import Path
from typing import Union, Dict, Callable

import cloup

PathType = Union[str, Path]


class LazyLoaded:
    def __init__(self, name: str, path: PathType, obj_name: str):
        """This is a proxy for a command defined in a file that is not loaded until
        it's actually needed.

        Args:
            name: name of the command.
            path: path of the file where the command is defined.
            obj_name: name of the command object inside the file.
        """
        self.name = name
        self.path = Path(path)
        self.obj_name = obj_name
        self._command = None

    @property
    def command(self):
        if self._command is None:
            self._command = cmd = self.load()
            return cmd
        return self._command

    def load(self):
        with open(self.path, encoding="utf8") as f:
            ns = {}
            code = compile(f.read(), self.path.name, 'exec')
            eval(code, ns, ns)
            return ns[self.obj_name]

    def __getattr__(self, item):
        return getattr(self.command, item)


class LazyGroup(LazyLoaded, cloup.Group):  # type: ignore
    pass


class LazyCommand(LazyLoaded, cloup.Command):  # type: ignore
    pass


def commands_in_folder(
    dir_path: PathType,
    get_obj_name: Callable[[str], str] = lambda name: name
) -> Dict[str, cloup.BaseCommand]:
    """Loads commands from a folder. Each commands must be in its own file.
    Files containing Group's must end with "__group".
    Returns a dictionary {name: lazy_command}."""
    dir_path = Path(dir_path)
    commands: Dict[str, cloup.BaseCommand] = {}
    for path in dir_path.glob("[!_]*.py"):
        fname = path.stem
        if fname.endswith("__group"):
            name = fname[:-len("__group")]
            commands[name] = LazyGroup(name, path, get_obj_name(name))
        else:
            commands[fname] = LazyCommand(fname, path, get_obj_name(fname))
    return commands


lazy_commands = commands_in_folder("commands")
# Now you can use lazy_command[name] as a normal command.


@cloup.group(commands=lazy_commands)   # type: ignore
def main():
    print("This is main")


if __name__ == '__main__':
    main()
