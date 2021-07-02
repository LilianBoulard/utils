import os
from pathlib import Path
from argparse import ArgumentParser

from typing import Optional


def get_line_count_of_file(file: Path) -> int:
    with open(file, 'r') as fl:
        count = len(fl.readlines())
    return count


def get_line_count_of_dir(dir: Path) -> int:
    total_lines = 0
    for child in dir.iterdir():
        if child.is_dir():
            total_lines += get_line_count_of_dir(child)
        else:
            total_lines += get_line_count_of_file(child)
    return total_lines


def scan(path: Path) -> Optional[int]:
    if path.is_file():
        return get_line_count_of_file(path)
    elif path.is_dir():
        return get_line_count_of_dir(path)
    else:
        print(f'Could not scan {path}')
        return


_parser = ArgumentParser(
    'A small utility for counting how many lines are in a file or the files of a directory.'
)

_parser.add_argument("-s", "--source",
                     help="The path, relative or absolute, "
                          "to the directory or file to scan. "
                          "If not specified, scans the current working directory",
                     nargs=1, type=str)


_args = _parser.parse_args()

if _args.source:
    source = _args.source[0]
else:
    source = os.getcwd()


if __name__ == "__main__":
    path = Path(source)
    print(f'{scan(path)} lines found in {source!r}')
