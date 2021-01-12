# flake8: noqa E128
import cloup
from cloup import Section


def make_example_group(align_sections):
    def f(**kwargs):
        print(**kwargs)

    git_clone = cloup.command(
        'clone', help='Clone a repository into a new directory')(f)
    git_hidden1 = cloup.command(
        'hidden1', hidden=True)(f)
    git_init = cloup.command(
        'init', help='Create an empty Git repository or reinitialize an existing one')(f)

    git_rm = cloup.command(
        'rm', help='Remove files from the working tree and from the index')(f)
    git_sparse_checkout = cloup.command(
        'sparse-checkout', help='Initialize and modify the sparse-checkout')(f)
    git_mv = cloup.command(
        'mv', help='Move or rename a file, a directory, or a symlink')(f)

    @cloup.group(
        'git', align_sections=align_sections, context_settings={'terminal_width': 80})
    def git():
        return 0

    # We'll add commands/sections in all possible ways
    first_section = git.section(
        'Start a working area (see also: git help tutorial)', git_init, git_hidden1)
    first_section.add_command(git_clone)

    git.add_section(Section(
        'Work on the current change (see also: git help everyday)',
        [git_rm, git_sparse_checkout, git_mv],
        sorted=True
    ))

    git.add_command(cloup.command('fake-3', hidden=True)(f))
    git.add_command(cloup.command('fake-2', help='Fake command #2')(f))
    git.add_command(cloup.command('fake-1', help='Fake command #1')(f))

    git.expected_help = (EXPECTED_ALIGNED_HELP if align_sections
                         else EXPECTED_NON_ALIGNED_HELP)
    return git


EXPECTED_ALIGNED_HELP = """
Usage: git [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Start a working area (see also: git help tutorial):
  init             Create an empty Git repository or reinitialize an existing...
  clone            Clone a repository into a new directory

Work on the current change (see also: git help everyday):
  mv               Move or rename a file, a directory, or a symlink
  rm               Remove files from the working tree and from the index
  sparse-checkout  Initialize and modify the sparse-checkout

Other commands:
  fake-1           Fake command #1
  fake-2           Fake command #2
""".strip()

EXPECTED_NON_ALIGNED_HELP = """
Usage: git [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Start a working area (see also: git help tutorial):
  init   Create an empty Git repository or reinitialize an existing one
  clone  Clone a repository into a new directory

Work on the current change (see also: git help everyday):
  mv               Move or rename a file, a directory, or a symlink
  rm               Remove files from the working tree and from the index
  sparse-checkout  Initialize and modify the sparse-checkout

Other commands:
  fake-1  Fake command #1
  fake-2  Fake command #2
""".strip()


if __name__ == '__main__':
    make_example_group(True)(['--help'])
