"""

This script constructs a tree from the output of any script that lists files.

Vocabulary:
- A ``node`` is a directory representation.
- A ``leaf`` is a file representation.

"""

import os

from time import time
from typing import List
from pathlib import Path
from warnings import warn
from argparse import ArgumentParser


class StorageTreeDirectory:

    def __init__(self, path: str, name: str, parent, level: int):
        self.path: str = path
        self.name: str = name
        self.parent = parent
        self.children: list = []
        self.size: int = 0
        self.view = self.parent.view
        self.level: int = level
        self.nb_results = self.parent.nb_results

    def __repr__(self):
        if display_mode == 'directory' or display_mode == 'file':
            return self.view.std_repr(self)
        else:
            return ''

    def child(self, child):
        """
        Creates a new child, and returns it.
        """
        self.children.append(child)
        return child

    def increment_size(self, inc: int) -> None:
        """
        Increments this directory's size of ``inc`` bytes.

        :param int inc: A size, in bytes.
        """
        self.size += inc

    def compute_size(self) -> int:
        """
        Compute the size of this directory by summing the sizes of its
        child directories and files.

        :return int: The size, in bytes, of this directory.
        """
        for child in self.children:
            if isinstance(child, StorageTreeDirectory):
                self.increment_size(child.compute_size())
            elif isinstance(child, StorageTreeFile):
                self.increment_size(child.size)
        return self.size


class StorageTreeFile:

    def __init__(self, path: Path, size: int, parent: StorageTreeDirectory, result_index: int):
        self.path: Path = path
        self.name: str = path.name
        self.size: int = size
        self.parent = parent
        self.level: int = len(path.parts) - 1
        self.index: int = result_index
        self.nb_results = self.parent.nb_results

    def __repr__(self):
        if display_mode == 'file':
            return self.parent.view.stf_repr(self)
        else:
            return ''


class StorageTree:

    def __init__(self, pydu_report_file: Path, parser_name: str, view_name: str):
        parser_file = __import__(f'parsers.{parser_name}', fromlist=['parsers'])
        view_file = __import__(f'views.{view_name}', fromlist=['views'])

        self._ran = False

        self.parser = parser_file.Parser(pydu_report_file)
        self.view = view_file.View()

        self.nb_results = len(self.parser.content)
        self.root = StorageTreeDirectory(
            path='',
            name=self.parser.root,
            parent=self,
            level=0,
        )

    def __repr__(self):
        if not self._ran:
            s = "This tree is empty. To construct it, use the ``run()`` method."
            warn(s)
            return s
        return self.view.st_repr(self)

    def run(self) -> None:
        """
        Launches the tree construction.
        """
        print(f'Constructing tree, adding {len(self.parser.content)} paths')
        t = time()

        def get_first_divergence_index(p1: Path, p2: Path) -> int:
            if (not p1) or (not p2):
                return 0
            for i, (a, b) in enumerate(zip(p1.parts, p2.parts)):
                if a != b:
                    return i

        last_leaf_path = None
        # We will begin at the root node
        current_node = self.root
        for current_leaf_path, current_leaf_size in self.parser.content.items():
            # At the beginning of the loop:
            # - We are not at the right place, so we'll have to navigate to our destination
            # - We have the info of the last leaf, giving us a point of reference
            # We must:
            # - Navigate to our destination:
            #   - We can compute the first divergence index, and navigate to it

            # First, given the last leaf, we'll compute the first divergence point,
            # meaning the first place where we change directory.
            divergence_index = get_first_divergence_index(current_leaf_path, last_leaf_path)

            # Now that we have the index, we'll compare our current depth to it,
            # and navigate accordingly.
            if current_node.level > divergence_index:
                # We are in a lower directory, we need to go up the tree.
                # Compute the difference
                diff = current_node.level - divergence_index
                for _ in range(diff):
                    current_node = current_node.parent
            elif current_node.level < divergence_index:
                # We are in an upper directory, we need to go down,
                # and the next part will take care of that.
                pass
            elif current_node.level == divergence_index:
                # We are already in the right directory, great !
                pass

            # Now that we are in the good node, we'll steep down.
            # Get the nodes from the divergence index to the leaf (exclusive).
            parts = current_leaf_path.parts[divergence_index:-1]
            for i, p in enumerate(parts):
                level = divergence_index + i + 1
                path = os.sep.join(current_leaf_path.parts[:level])
                #print(level, path)
                current_node = current_node.child(
                    StorageTreeDirectory(
                        path=path,
                        name=p,
                        parent=current_node,
                        level=level
                    )
                )
            else:
                # After all the parts were added,
                # we add the leaf.
                current_node.child(
                    StorageTreeFile(
                        path=current_leaf_path,
                        size=current_leaf_size,
                        parent=current_node,
                        result_index=0  # TODO
                    )
                )

            last_leaf_path = current_leaf_path

        print(f'Done constructing tree, took {time() - t:.3f}s')

        print('Computing sizes')
        t = time()

        self.compute_dirs_sizes()
        self._ran = True

        print(f'Done computing sizes, took {time() - t:.3f}s')

    def compute_dirs_sizes(self) -> int:
        """
        Triggers the size computation for all directories.
        A directory's size is the sum of its children's sizes.

        :return int: The total size of the tree.
        """
        return self.root.compute_size()


def get_available_parsers() -> List[str]:
    files = os.listdir('parsers')
    # For each file, remove the extension if it's a Python script.
    parsers = [f[:-3] for f in files if f.endswith('.py')]
    parsers.pop(parsers.index('base'))
    return parsers


def get_available_views() -> List[str]:
    files = os.listdir('views')
    # For each file, remove the extension if it's a Python script.
    views = [f[:-3] for f in files if f.endswith('.py')]
    views.pop(views.index('base'))
    return views


_available_parsers = get_available_parsers()
_available_views = get_available_views()


_parser = ArgumentParser()

_parser.add_argument("-s", "--source",
                     help="The path to the source file to parse. ",
                     required=True, nargs=1, type=str)
_parser.add_argument("-p", "--parser",
                     help=f"The parser used on the source file. "
                          f"Available parsers: {_available_parsers}.",
                     required=True, nargs=1, type=str)
_parser.add_argument("-v", "--view",
                     help=f"The view used to visualize the data. "
                          f"Available views: {_available_views}. "
                          f"Note: output will be directed to stdout.",
                     required=True, nargs=1, type=str)
_parser.add_argument("-o", "--output",
                     help=f"A path to the file where the results "
                          f"of the storage tree will be extracted.",
                     required=True, nargs=1, type=str)
_parser.add_argument("--per",
                     help="Display setting. Can be any of {'directory', 'file'}. "
                          "'directory' will only display directories, "
                          "'file' will display both directory and files tree. "
                          "Default is 'file'.",
                     required=False, nargs=1, type=str)

_args = _parser.parse_args()

result_file = Path(_args.source[0]).resolve()
if not result_file.is_file():
    raise ValueError(f"File {result_file!r} does not exist!")

parser = _args.parser[0]
assert parser in _available_parsers, \
    f"Specified parser is invalid ({parser}), " \
    f"select one from the following: {_available_parsers}"

view = _args.view[0]
assert view in _available_views, \
    f"Specified view is invalid ({view}), " \
    f"select one from the following: {_available_views}"

output_file = Path(_args.output[0]).resolve()

if _args.per:
    display_mode = _args.per[0]
else:
    display_mode = 'file'


if __name__ == "__main__":
    storage_tree = StorageTree(result_file, parser, view)
    storage_tree.run()
    with open(output_file, 'w') as fl:
        fl.write(repr(storage_tree))
