import os
import shutil
from glob import glob
import argparse
from itertools import chain

parser = argparse.ArgumentParser(
    description="""
    Remove full directories and files matching the provided glob patterns.

    If -r/--recursive, the pattern '**' will match any files and zero or more
    directories and subdirectories.
    """
)
parser.add_argument('paths', nargs='+')
parser.add_argument('-r', '--recursive', action='store_true',
                    help="Use recursive globs, i.e. the pattern '**' will match any "
                         "files and zero or more directories and subdirectories.")
parser.add_argument('-d', '--dry-run', action='store_true',
                    help='Do not remove files, just print a list of them')

args = parser.parse_args()

paths = set(chain.from_iterable(
    glob(arg, recursive=args.recursive)
    for arg in args.paths
))

if args.dry_run:
    print('\n'.join(paths))
else:
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        print('Removed', path)
