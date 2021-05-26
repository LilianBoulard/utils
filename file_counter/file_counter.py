import os
from argparse import ArgumentParser


def get_files_count_by_dir() -> int:
    total_files = 0
    for root, subdirs, files in os.walk(directory):
        total_files += len(files)
        if count_dirs:
            total_files += len(subdirs)

    return total_files


_parser = ArgumentParser(
    'A small utility for counting how many files there are in a directory.'
)

_parser.add_argument("-d", "--directory",
                     help="The path, relative or absolute, "
                          "to the directory to scan. If not specified, "
                          "scans the current working directory",
                     required=True, nargs=1, type=str)
_parser.add_argument("--count_dirs",
                     help="If directories should be counted. "
                          "False by default, specify for True.",
                     action="store_true")


_args = _parser.parse_args()

if _args.directory:
    directory = _args.directory[0]
else:
    directory = os.getcwd()

if _args.count_dirs:
    count_dirs = True
else:
    count_dirs = False


print(get_files_count_by_dir())
