from typing import Callable, Dict, Iterator, Optional

import click
from click._compat import strip_ansi

import cloup


def preorder_visit(
    cmd: cloup.Command, prog_name: Optional[str] = None
) -> Iterator[cloup.Context]:
    """Iterates the commands in a command tree in pre-order. This function yields
    ``Context`` objects rather than commands, because a ``Context`` is needed
    anyway to call most useful methods of commands. The command is accessible in
    the ``ctx.command`` argument. The returned contexts are all linked using the
    ``parent`` attribute to make all methods work properly."""
    ctx = cloup.Context(command=cmd, info_name=prog_name or cmd.name)
    return _preorder_visit(ctx)


def _preorder_visit(ctx: cloup.Context) -> Iterator[cloup.Context]:
    yield ctx
    cmd = ctx.command
    if isinstance(cmd, click.MultiCommand):
        subcommand_names = cmd.list_commands(ctx)
        for name in subcommand_names:
            subcommand = cmd.get_command(ctx, name)
            child_ctx = cloup.Context(command=subcommand, info_name=name, parent=ctx)
            yield from _preorder_visit(child_ctx)


def command_to_markdown(
    command: click.Command,
    command_formatter: Callable,
    header_level=1,
    section_sep='\n\n',
    include_toc: bool = True,
    prog_name: Optional[str] = None,
) -> str:
    section_list = []
    if include_toc:
        toc = build_markdown_toc(command, prog_name)
        section_list.append(toc)
    for ctx in preorder_visit(command, prog_name):
        command_path = ctx.command_path
        level = header_level + len(command_path.split())
        header_start = '#' * (level - 1)
        title = f"{header_start} `{command_path}`"
        help_text = command_formatter(ctx, level)
        section = title + '\n' + help_text
        section_list.append(section)
    return section_sep.join(section_list)


def build_markdown_toc(
    command: click.Command,
    prog_name: Optional[str] = None,
    header_level: int = 1,
) -> str:
    lines = ["#" * header_level + " Table of contents"]
    for ctx in preorder_visit(command, prog_name):
        command_path = ctx.command_path
        level = len(command_path.split()) - 1
        indentation = "   " * level
        line = f"{indentation}- {markdown_link(command_path)}"
        lines.append(line)
    return '\n'.join(lines)


def markdown_link(command_path: str) -> str:
    return f"[{command_path}](#{get_command_anchor_name(command_path)})"


def get_command_anchor_name(command_path: str) -> str:
    return command_path.replace(" ", "-")


def get_command_anchor(command_path: str) -> str:
    return f'<a name={get_command_anchor_name(command_path)}></a>'


def to_markdown_plain(ctx: click.Context) -> str:
    """Just returns the --help output as string."""
    command = ctx.command
    help_text = command.get_help(ctx)
    return f'```\n{help_text}\n```'


def table_formatter(ctx: cloup.Context, level: int) -> str:
    """Uses markdown tables for options."""
    ctx.show_default = False
    command = ctx.command
    help_text = command.help.strip() if command.help else ""
    help_text = strip_ansi(help_text.replace('\b', ''))
    usage = command.get_usage(ctx)
    out = [f"```\n{usage}\n```"]
    if help_text:
        out.append(help_text)

    # Subcommands
    if isinstance(command, click.MultiCommand):
        subcommands = {name: command.get_command(ctx, name)
                       for name in command.list_commands(ctx)}
        cmd_table = make_markdown_table(
            header=("Subcommand", "Short description"),
            body=commands_to_rows(subcommands, ctx),
        )
        out.append("#" * level + " Subcommands")
        out.append(cmd_table)

    # Parameters
    params = command.get_params(ctx)
    opts = [p for p in params if p.param_type_name == "option"]
    if opts:
        opt_table = make_markdown_table(
            header=('Option', 'Description', 'Default'),
            body=options_to_rows(opts, ctx),
        )
        out.append("#" * level + " Options")
        out.append(opt_table)

    if command.epilog:
        out.append(command.epilog)
    return '\n\n'.join(out)


def make_markdown_table(header, body):
    body = [tuple(val.replace("|", r"\|") for val in row)
            for row in body]
    data_rows = [header] + body
    col_widths = [2 + max(map(len, col)) for col in zip(*data_rows)]
    md_rows = [markdown_table_row(row, col_widths) for row in data_rows]
    sep_row = '| ' + ' | '.join('-' * (width - 2) for width in col_widths) + ' |'
    table = '\n'.join([md_rows[0], sep_row, *md_rows[1:]])
    return table


def options_to_rows(opts, ctx):
    rows = []
    for opt in opts:
        opt.show_default = False
        opt_name, opt_help = opt.get_help_record(ctx)
        opt_default = opt.get_default(ctx)
        opt_default = (f'"{opt_default}"' if isinstance(opt_default, str)
                       else str(opt_default))
        rows.append((f"`{opt_name}`", opt_help, f"`{opt_default}`"))
    return rows


def commands_to_rows(commands: Dict[str, cloup.Command], ctx: cloup.Context) -> str:
    rows = []
    for name, cmd in commands.items():
        short_help = cmd.get_short_help_str(80)
        command_path = f"{ctx.command_path} {name}"
        rows.append((markdown_link(command_path), short_help))
    return rows


def markdown_table_row(values, col_widths):
    strings = (f' {value:<{w - 1}s}' for w, value in zip(col_widths, values))
    return '|' + '|'.join(strings) + '|'
