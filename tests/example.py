import cloup
from cloup import option_group


@cloup.command('example')
@option_group('Option group A', [
    cloup.option('--a1', help='1st option of group A'),
    cloup.option('--a2', help='2nd option of group A'),
    cloup.option('--a3', help='3rd option of group A')],
    help='This is a useful description of group A',
)
@option_group('Option group B', [
    cloup.option('--b1', help='1st option of group B'),
    cloup.option('--b2', help='end option of group B'),
    cloup.option('--b3', help='3rd option of group B'),
])
@cloup.option('--opt1', help='an uncategorized option')
@cloup.option('--opt2', help='another uncategorized option')
def cli(**kwargs):
    """ A CLI that does nothing. """
    print(kwargs)


if __name__ == '__main__':
    cli()
