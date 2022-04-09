"""
This example:
- requires click-default-group
- was written in response to a StackOverflow question, not because I think it's
  a good idea to have groups with default command; I tend to not recommend them.
"""
import click

import cloup
from click_default_group import DefaultGroup


class GroupWithDefaultCommand(cloup.Group, DefaultGroup):
    # (Optional) Mark the default command with "*". If you don't need this, you
    # can just write `pass`.
    def format_subcommand_name(
        self, ctx: click.Context, name: str, cmd: click.Command
    ) -> str:
        if name == self.default_cmd_name:
            name = name + "*"
        return super().format_subcommand_name(ctx, name, cmd)


@cloup.group(cls=GroupWithDefaultCommand, default='alice')
def cli():
    pass


@cli.command()
@cloup.option("--foo")
def alice(**kwargs):
    print("Called alice with", kwargs)


@cli.command()
@cloup.option("--bar")
def bob(**kwargs):
    print("Called bob with", kwargs)


if __name__ == '__main__':
    cli()
