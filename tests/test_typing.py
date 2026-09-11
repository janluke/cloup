"""Public typing contracts, checked by MyPy and executable with pytest."""

# mypy: warn-unused-ignores

from typing import TYPE_CHECKING, Any, get_type_hints

import click
import pytest
from click.testing import CliRunner
from typing_extensions import assert_type

import cloup


class CustomCommand(cloup.Command):
    def __init__(self, *, custom: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.custom = custom


class CustomGroup(cloup.Group):
    def __init__(self, *, custom: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.custom = custom


def callback() -> None:
    pass


def test_command_decorator_types() -> None:
    assert_type(cloup.command()(callback), cloup.Command)
    assert_type(cloup.command(cls=None)(callback), cloup.Command)
    cmd = cloup.command(cls=CustomCommand, custom=True)(callback)
    assert_type(cmd, CustomCommand)
    assert cmd.custom
    assert_type(cloup.command(cls=click.Command)(callback), click.Command)

    assert_type(cloup.group()(callback), cloup.Group)
    assert_type(cloup.group(cls=None)(callback), cloup.Group)
    grp = cloup.group(cls=CustomGroup, custom=True)(callback)
    assert_type(grp, CustomGroup)
    assert grp.custom
    assert_type(cloup.group(cls=click.Group)(callback), click.Group)


def test_subcommand_decorator_types() -> None:
    parent = cloup.Group("parent")
    # Defaults can be customized through command_class and group_class, so
    # the inferred types must allow arbitrary Click commands and groups.
    cmd = parent.command("default")(callback)
    assert_type(cmd, click.Command)
    assert isinstance(cmd, cloup.Command)
    custom_cmd = parent.command("custom", cls=CustomCommand, custom=True)(callback)
    assert_type(custom_cmd, CustomCommand)
    assert custom_cmd.custom
    grp = parent.group("default-group", cls=None)(callback)
    assert_type(grp, click.Group)
    assert isinstance(grp, cloup.Group)
    custom_grp = parent.group("custom-group", cls=CustomGroup, custom=True)(callback)
    assert_type(custom_grp, CustomGroup)
    assert custom_grp.custom


def test_group_inherited_keyword_types() -> None:
    grp = cloup.group(
        formatter_settings=None,
        align_option_groups=True,
        show_constraints=True,
        params=[cloup.Option(["--value"])],
    )(callback)
    assert_type(grp, cloup.Group)
    child = grp.group(
        "child",
        formatter_settings=None,
        align_option_groups=True,
        show_constraints=True,
        params=[cloup.Option(["--other"])],
    )(callback)
    assert_type(child, click.Group)
    assert child.params[0].name == "other"


def test_parameter_decorators_preserve_callback_types() -> None:
    def convert(value: str) -> int:
        return int(value, 16)

    def typed_callback(value: int) -> str:
        return str(value)

    option_callback = cloup.option("--value", type=convert)(typed_callback)
    argument_callback = cloup.argument("value", cls=click.Argument)(typed_callback)
    # Comparing calls also checks that argument and return types survive decorating.
    assert_type(option_callback(1), str)
    assert_type(argument_callback(value=2), str)
    assert option_callback(1) == "1"
    assert argument_callback(2) == "2"

    @cloup.command()
    @cloup.option("--value", type=(convert, cloup.INT), show_default="hex and int")
    @cloup.argument("label", cls=cloup.Argument, type=str)
    def cmd(value: tuple[int, int], label: str) -> None:
        click.echo(f"{label}: {value}")

    result = CliRunner().invoke(cmd, ["--value", "ff", "2", "pair"])
    assert result.exit_code == 0
    assert result.output == "pair: (255, 2)\n"
    assert "hex and int" in CliRunner().invoke(cmd, ["--help"]).output

    cloup.option("--enabled", type=bool, show_default=None)
    cloup.option("--choice", type=cloup.Choice([1, 2]))


def test_option_group_attribute_type() -> None:
    group = cloup.OptionGroup("Options")
    option = cloup.Option(["--value"], group=group)
    assert_type(option.group, cloup.OptionGroup | None)
    assert option.group is group


def test_formatter_write_accepts_click_keyword() -> None:
    formatter = cloup.HelpFormatter()
    click_formatter: click.HelpFormatter = formatter
    click_formatter.write(string="first")
    formatter.write(" second", " third")
    formatter.write()
    assert formatter.getvalue() == "first second third"


def test_context_types() -> None:
    ctx = cloup.Context(cloup.Command("cmd"))
    with ctx:
        assert_type(cloup.get_current_context(), cloup.Context)
        assert_type(cloup.get_current_context(False), cloup.Context)
        assert_type(cloup.get_current_context(silent=False), cloup.Context)
        assert_type(cloup.get_current_context(True), cloup.Context | None)
        assert cloup.get_current_context(False) is ctx
    assert cloup.get_current_context(silent=True) is None
    with pytest.raises(RuntimeError):
        cloup.get_current_context(False)


def test_pass_context_preserves_signature() -> None:
    @cloup.pass_context
    def func(ctx: cloup.Context, value: int, *, suffix: str) -> str:
        return f"{ctx.command.name}: {value}{suffix}"

    with cloup.Context(cloup.Command("cmd")):
        assert_type(func(1, suffix="!"), str)
        assert func(1, suffix="!") == "cmd: 1!"

    # ParamSpec and Concatenate are available at runtime on Python 3.10+.
    assert get_type_hints(cloup.pass_context)["return"] is not None


if TYPE_CHECKING:

    def check_rejected_calls(silent: bool) -> None:
        assert_type(cloup.get_current_context(silent), cloup.Context | None)
        parent = cloup.Group("parent")
        parent.group(unknown=True)  # type: ignore[call-overload]
        parent.group(cls=None, unknown=True)  # type: ignore[call-overload]
        cloup.option("--value", show_default=123)  # type: ignore[call-overload]

        @cloup.pass_context
        def func(ctx: cloup.Context, value: int) -> str:
            return str(value)

        func("wrong")  # type: ignore[arg-type]
        func()  # type: ignore[call-arg]
