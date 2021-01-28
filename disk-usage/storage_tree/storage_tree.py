# -*- coding: utf-8 -*-

"""

This script constructs a size tree from the output of a disk-usage (disk_usage.py).
Some values are hard-coded from the specifications of this disk usage script.

Vocabulary:
- A ``node`` is a directory representation.
- A ``leaf`` is a file representation.

"""

import os

from argparse import ArgumentParser
from warnings import warn


def human_readable_bytes(size: int) -> str:
    """
    Takes a size in bytes and returns a readable.

    :param int size: A size, in bytes.
    :return str: A readable size. e.g. 5 GB, 14 MB, 1 TB...
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size >= 1024:
        size /= 1024
        unit_index += 1
    b = units[unit_index]  # Could raise an IndexError if the file size is above or equal to 1024TB.
    size = f"{int(size)} {b}"
    return size


class View:

    """
    To create a new view (a new way of visualizing the tree),
    copy this class and fill in the three following functions.
    """

    @staticmethod
    def std_repr(obj) -> str:
        """
        :param StorageTreeDirectory obj:
        :return str:
        """
        raise NotImplemented("Override the View class to add your custom view.")

    @staticmethod
    def stf_repr(obj) -> str:
        """
        :param StorageTreeFile obj:
        :return str:
        """
        raise NotImplemented("Override the View class to add your custom view.")

    @staticmethod
    def st_repr(obj) -> str:
        """
        :param StorageTree obj:
        :return str:
        """
        raise NotImplemented("Override the View class to add your custom view.")


class StorageTreeDirectory:
    def __init__(self, name: str, parent, level: int):
        self.name: str = name
        self.parent = parent
        self.children: list = []
        self.size: int = 0
        self.view = self.parent.view
        self.level: int = level
        self.nb_results = self.parent.nb_results

    def __repr__(self):
        return self.view.std_repr(self)

    def child(self, child):
        """
        Returns a child (node or leaf).
        Creates it if it doesn't already exist.

        :param StorageTreeDirectory|StorageTreeFile child:
        :return StorageTreeDirectory|StorageTreeFile:
        """
        for ch in self.children:
            if ch.name == child.name:
                return ch
        else:
            # Gets executed at the end of the for loop, if no corresponding child has been found.
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
        Compute the size of this directory by summing the sizes of its child directories and files.

        :return int: The size, in bytes, of this directory.
        """
        for child in self.children:
            if isinstance(child, StorageTreeDirectory):
                self.increment_size(child.compute_size())
            elif isinstance(child, StorageTreeFile):
                self.increment_size(child.size)
        return self.size


class StorageTreeFile:
    def __init__(self, path: str, name: str, size: int, parent: StorageTreeDirectory, level: int, result_index: int):
        self.path: str = path
        self.name: str = name
        self.size: int = size
        self.parent = parent
        self.level: int = level
        self.index: int = result_index
        self.nb_results = self.parent.nb_results

    def __repr__(self):
        return self.parent.view.stf_repr(self)


class StorageTree:
    def __init__(self, pydu_report_file: str, view=View):
        self.view = view
        self.ran = False

        with open(pydu_report_file, "r+") as f:
            self.results = f.readlines()

        # Pop the last line, which is the expected length.
        supposed_length = self.results.pop(-1)  # The last line contains the number of results the script returned.

        self.nb_results = len(self.results)

        if not self.nb_results == int(supposed_length):
            # The announced length and the actual length do not correspond.
            raise ValueError(f"Incorrect PyDU file format: expected {supposed_length} lines, got {self.nb_results}.")

        # Init the root node

        # Gets the directory root.
        # For instance, the root is "storage" in "/storage/of/server/".
        root = self.tuple_string_to_tuple_object(self.results[0])[0].split(os.sep)[0]
        self.root = StorageTreeDirectory(root, self, level=0)

    def __repr__(self):
        if not self.ran:
            s = "This tree is empty. To construct it, use the ``run()`` method on the instance."
            warn(s)
            return s
        return self.view.st_repr(self)

    @staticmethod
    def tuple_string_to_tuple_object(v: str) -> tuple:
        """
        Takes a string formatted like a tuple, and returns an actual tuple.

        :param str v: A stringed-tuple.
        :return tuple:
        """
        # Removes special characters.
        v = v.replace("(", "")
        v = v.replace(")", "")
        v = v.replace("'", "")
        return tuple(v.split(", "))

    def run(self) -> None:
        """
        Launches the tree construction.
        """
        for index, file_info in enumerate(self.results):
            path, size = self.tuple_string_to_tuple_object(file_info)
            self.add_leaf(path, int(size), index)

        self.compute_dirs_sizes()
        self.ran = True

    def add_leaf(self, path: str, size: int, result_index: int) -> None:
        """
        Adds a new leaf (file) to the tree.
        It creates the nodes (directories) on the fly.

        :param str path: Absolute path to the file.
        :param int size: Size of the file to add to the tree.
        :param int result_index: From 0 to ``n``-1 (``n`` being the total number of lines in the PyDU output).
        The file index 0 is the heaviest.
        """
        l_path = path.split(os.sep)
        st = self.root
        # We skip the first, as it's the root, and the last, as it's the file.
        for index, dir_name in enumerate(l_path[1:-1]):
            st = st.child(StorageTreeDirectory(dir_name, st, level=index + 1))
        else:
            file_name = l_path[-1]
            level = len(l_path) - 1
            st.child(StorageTreeFile(path, file_name, size, st, level, result_index))

    def compute_dirs_sizes(self) -> int:
        """
        Triggers the size computation for all directories.
        A directory's size is the sum of its children's sizes.

        :return int: The total size of the tree.
        """
        return self.root.compute_size()


parser = ArgumentParser()

parser.add_argument("-s", "--source",
                    help="The path to the file generated by the PyDU script.",
                    required=True, nargs=1, type=str)

args = parser.parse_args()

pydu_result_file = args.source[0]
if not os.path.isfile(pydu_result_file):
    raise ValueError(f"File {pydu_result_file!r} does not exist!")


if __name__ == "__main__":
    storage_tree = StorageTree(pydu_result_file)
    storage_tree.run()
    # print(storage_tree)  # Print will not work as it uses the default view.
