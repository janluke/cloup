import click
import cloup
from cloup import option_group, option


@cloup.command('clouptest')
@click.argument('arg', required=False)
@option_group('Option group A', [
    option('--a1', help='1st option of group A'),
    option('--a2', help='2nd option of group A'),
    option('--a3', help='3rd option of group A')],
    help='This is a useful description of group A',
)
@option_group('Option group B', [
    option('--b1', help='1st option of group B'),
    option('--b2', help='2nd option of group B'),
    option('--b3', help='3rd option of group B', hidden=True),
])
@option('--opt1', help='uncategorized option #1')
@option('--opt2', help='uncategorized option #2', hidden=True)
@option('--opt3', help='uncategorized option #3')
def example_cli(**kwargs):
    """ A CLI that does nothing. """
    print(kwargs)


if __name__ == '__main__':
    example_cli()
