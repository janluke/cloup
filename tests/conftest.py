from click.testing import CliRunner
from pytest import fixture

from tests.example_command import make_example_command
from tests.example_group import make_example_group


@fixture()
def runner():
    return CliRunner()


@fixture(scope='session')
def get_example_command():
    aligned_cmd = make_example_command(align_option_groups=True)
    non_aligned_cmd = make_example_command(align_option_groups=False)

    def get_command(align_option_groups):
        return aligned_cmd if align_option_groups else non_aligned_cmd

    return get_command


@fixture(scope='session')
def get_example_group():
    aligned_cmd = make_example_group(align_sections=True)
    non_aligned_cmd = make_example_group(align_sections=False)

    def get_group(align_sections):
        return aligned_cmd if align_sections else non_aligned_cmd

    return get_group
