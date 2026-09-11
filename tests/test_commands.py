import re

import click
import pytest

import cloup
from cloup._util import reindent
from cloup.constraints import mutually_exclusive
from tests.util import new_dummy_func


def test_command_handling_of_unknown_argument():
    with pytest.raises(TypeError, match="Hint: you set `cls="):
        cloup.command(cls=click.Command, align_option_groups=True)(new_dummy_func())
    with pytest.raises(TypeError, match="nonexisting") as info:
        cloup.command(nonexisting=True)(new_dummy_func())
    assert re.search(str(info.value), "Hint") is None


def test_group_raises_if_cls_is_not_subclass_of_click_Group():
    cloup.group()
    cloup.group(cls=click.Group)
    cloup.group(cls=cloup.Group)
    with pytest.raises(TypeError):
        cloup.group(cls=click.Command)


def test_group_handling_of_unknown_argument():
    with pytest.raises(TypeError, match="Hint"):
        cloup.group(cls=click.Group, align_sections=True)(new_dummy_func())
    with pytest.raises(TypeError) as info:
        cloup.group(unexisting_arg=True)(new_dummy_func())
    assert re.search(str(info.value), "Hint") is None


def test_command_works_with_no_parameters(runner):
    cmd = cloup.Command(name="cmd", callback=new_dummy_func())
    res = runner.invoke(cmd, "--help")
    assert res.output == reindent(
        """
        Usage: cmd [OPTIONS]

        Options:
          --help  Show this message and exit.
        """
    )


def test_group_works_with_no_params_and_subcommands(runner):
    cmd = cloup.Group(name="cmd")
    res = runner.invoke(cmd, "--help")
    assert res.output == reindent(
        """
        Usage: cmd [OPTIONS] COMMAND [ARGS]...

        Options:
          --help  Show this message and exit.
        """
    )


@pytest.mark.parametrize(
    "decorator, usage_args",
    [
        (cloup.command, "[OPTIONS]"),
        (cloup.group, "[OPTIONS] COMMAND [ARGS]..."),
    ],
)
@pytest.mark.parametrize(
    "help_text, expected_help",
    [
        (None, ""),
        ("", ""),
        ("Do a thing.", "Do a thing."),
        (
            "First paragraph.\n\nSecond paragraph.",
            "First paragraph.\n\n  Second paragraph.",
        ),
        ("\n    Do a thing.\n    On another line.", "Do a thing. On another line."),
        ("Visible text.\fHidden text.", "Visible text."),
    ],
)
@pytest.mark.parametrize(
    "deprecated, expected_label",
    [
        (False, ""),
        (True, "(DEPRECATED)"),
        ("", ""),
        ("use `newcmd` instead", "(DEPRECATED: use `newcmd` instead)"),
    ],
)
def test_deprecated_command_help(
    runner,
    decorator,
    usage_args,
    help_text,
    expected_help,
    deprecated,
    expected_label,
):
    cmd = decorator(name="example", help=help_text, deprecated=deprecated)(
        new_dummy_func()
    )

    result = runner.invoke(cmd, ["--help"], terminal_width=80)

    assert result.exit_code == 0
    body = " ".join(part for part in (expected_help, expected_label) if part)
    expected_output = f"Usage: example {usage_args}\n"
    if body:
        expected_output += f"\n  {body}\n"
    expected_output += "\nOptions:\n  --help  Show this message and exit.\n"
    assert result.output == expected_output


@pytest.mark.parametrize("decorator", [cloup.command, cloup.group])
def test_deprecated_command_help_keeps_theme(runner, decorator):
    @decorator(
        deprecated="use `newcmd` instead",
        formatter_settings={
            "theme": cloup.HelpTheme(
                command_help=cloup.Style(fg="yellow"),
            )
        },
    )
    def example():
        """Do a thing."""

    result = runner.invoke(example, ["--help"], color=True)
    assert result.exit_code == 0
    assert (
        click.style("Do a thing. (DEPRECATED: use `newcmd` instead)", fg="yellow")
        in result.output
    )


class TestDidYouMean:
    @staticmethod
    @pytest.fixture(scope="class")
    def cmd():
        cmd = cloup.Group(name="cmd")
        subcommands = [("install", ["ins"]), ("remove", ["rm"]), ("clear", [])]
        for name, aliases in subcommands:
            cmd.add_command(
                cloup.Command(name=name, aliases=aliases, callback=new_dummy_func())
            )
        return cmd

    def test_with_no_matches(self, runner, cmd):
        res = runner.invoke(cmd, "asdfdsgdfgdf")
        assert res.output == reindent(
            """
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'asdfdsgdfgdf'.
            """
        )

    def test_with_one_match(self, runner, cmd):
        res = runner.invoke(cmd, "clearr")
        assert res.output == reindent(
            """
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'clearr'. Did you mean 'clear'?
            """
        )

    def test_with_multiple_matches(self, runner, cmd):
        res = runner.invoke(cmd, "inst")
        assert res.output == reindent(
            """
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'inst'. (Did you mean one of: 'ins', 'install'?)
            """
        )

    def test_raises_click_no_such_command_with_alias_possibilities(self, cmd):
        with pytest.raises(click.NoSuchCommand) as exc_info:
            cmd.main(["inst"], prog_name="cmd", standalone_mode=False)

        assert exc_info.value.possibilities == ["ins", "install"]

    def test_token_normalization_preserves_fallback_behavior(self, runner):
        cmd = cloup.Group(
            name="cmd", context_settings={"token_normalize_func": str.lower}
        )
        cmd.add_command(
            cloup.Command(name="install", aliases=["ins"], callback=new_dummy_func())
        )

        res = runner.invoke(cmd, "INSS")

        assert res.output == reindent(
            """
            Usage: cmd [OPTIONS] COMMAND [ARGS]...
            Try 'cmd --help' for help.

            Error: No such command 'inss'.
            """
        )


@pytest.mark.parametrize(
    "decorator, cls",
    [(cloup.command, cloup.Command), (cloup.group, cloup.Group)],
)
def test_command_decorators_accept_cls_as_positional_argument(decorator, cls):
    class CustomClass(cls):
        pass

    @decorator("cmd", CustomClass)
    def cmd():
        pass

    assert isinstance(cmd, CustomClass)
    assert cmd.name == "cmd"


def test_group_subcommand_decorators_accept_cls_as_positional_argument():
    class CustomCommand(cloup.Command):
        pass

    class CustomGroup(cloup.Group):
        pass

    @cloup.group()
    def root():
        pass

    @root.command("sub-cmd", CustomCommand)
    def subcommand():
        pass

    @root.group("sub-grp", CustomGroup)
    def subgroup():
        pass

    assert isinstance(subcommand, CustomCommand)
    assert isinstance(subgroup, CustomGroup)
    assert root.commands == {"sub-cmd": subcommand, "sub-grp": subgroup}


@pytest.mark.parametrize(
    "decorator, expected_cls",
    [(cloup.command, cloup.Command), (cloup.group, cloup.Group)],
)
def test_command_decorators_can_be_used_without_parenthesis(decorator, expected_cls):
    @decorator
    def cmd_without_parenthesis():
        pass

    assert isinstance(cmd_without_parenthesis, expected_cls)
    # The callback takes the place of `name`, so the name is derived from it.
    assert cmd_without_parenthesis.name == "cmd-without-parenthesis"


def test_group_subcommand_decorators_can_be_used_without_parenthesis():
    @cloup.group()
    def root():
        pass

    @root.group
    def subgroup():
        pass

    @root.command
    def subcommand():
        pass

    assert isinstance(subgroup, cloup.Group)
    assert isinstance(subcommand, cloup.Command)
    assert root.commands == {"subgroup": subgroup, "subcommand": subcommand}


def test_command_decorators_without_parenthesis_support_constraints():
    @cloup.command
    @cloup.option("--one")
    @cloup.option("--two")
    @cloup.constraint(mutually_exclusive, ["one", "two"])
    def cmd(one, two):
        pass

    assert len(cmd.param_constraints) == 1


def test_group_command_class_is_used_to_create_subcommands(runner):
    class CustomCommand(cloup.Command):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("context_settings", {"help_option_names": ("--help", "-h")})
            super().__init__(*args, **kwargs)

    class CustomGroup(cloup.Group):
        command_class = CustomCommand

    @cloup.group("cli", cls=CustomGroup)
    def my_cli():
        pass

    @my_cli.command()
    def subcommand():
        pass

    assert isinstance(subcommand, CustomCommand)

    res = runner.invoke(my_cli, ["subcommand", "--help"])
    assert res.output == reindent(
        """
                Usage: cli subcommand [OPTIONS]

                Options:
                  -h, --help  Show this message and exit.
                """
    )


def test_group_class_is_used_to_create_subgroups(runner):
    class CustomGroup(cloup.Group):
        group_class = type

    class OtherCustomGroup(cloup.Group):
        group_class = cloup.Group

    @cloup.group("cli", cls=CustomGroup)
    def my_cli():
        pass

    @my_cli.group()
    def sub_group():
        pass

    @my_cli.group(cls=OtherCustomGroup)
    def other_group():
        pass

    @other_group.group()
    def other_sub_group():
        pass

    assert isinstance(sub_group, CustomGroup)
    assert isinstance(other_group, OtherCustomGroup)
    assert isinstance(other_sub_group, cloup.Group)


def test_click_positional_arguments_with_help_are_supported(runner):
    @cloup.command()
    @click.argument("input_path", help="Input path")
    def cmd(_):
        """Case B: click.argument(help=...) in a cloup command."""

    res = runner.invoke(cmd, ["--help"], prog_name="example")
    assert res.output == reindent(
        """
        Usage: example [OPTIONS] INPUT_PATH

          Case B: click.argument(help=...) in a cloup command.

        Positional arguments:
          INPUT_PATH  Input path

        Options:
          --help      Show this message and exit.
        """
    )


def test_deprecation_label_is_correctly_applied_to_cloup_arguments(runner):
    @cloup.command()
    @cloup.argument(
        "input_path", help="Input path", deprecated="use --path instead", required=False
    )
    def cmd(_):
        """A command."""

    res = runner.invoke(cmd, ["--help"], prog_name="example")
    assert res.output == reindent(
        """
        Usage: example [OPTIONS] [INPUT_PATH!]

          A command.

        Positional arguments:
          [INPUT_PATH!]  Input path (DEPRECATED: use --path instead)

        Options:
          --help         Show this message and exit.
        """
    )
