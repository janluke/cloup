from functools import partial

from click.testing import CliRunner
from pytest import fixture

from tests.example_command import make_example_command
from tests.example_group import make_example_group


@fixture()
def runner():
    runner = CliRunner()
    runner.invoke = partial(runner.invoke, catch_exceptions=False)
    return runner


@fixture(scope='session')
def get_example_command():
    def get_command(tabular_help=True, align_option_groups=True):
        return make_example_command(
            align_option_groups=align_option_groups, tabular_help=tabular_help)

    return get_command


@fixture(scope='session')
def get_example_group():
    def get_group(align_sections):
        return make_example_group(align_sections=align_sections)

    return get_group
