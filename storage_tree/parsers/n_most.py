from pathlib import Path
from typing import List, Dict

from .base import BaseParser


class Parser(BaseParser):

    """
    Used to parse the output of n_most.
    Example of expected input:

    ```
    ('/path/to/file3', 102410241024)
    ('/path/to/file2', 10241024)
    ('/path/to/file1', 1024)
    ```

    """

    ReadFileStructure = List[str]

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

    def _read_file(self) -> ReadFileStructure:
        with open(self.file, 'r') as fl:
            return fl.readlines()

    def _get_content(self) -> Dict[Path, int]:
        # Pop the last line, which is the expected length.
        supposed_length = self.raw_content.pop(-1)
        self.nb_results = len(self.raw_content)
        assert self.nb_results == int(supposed_length), \
            f"Incorrect PyDU file format: " \
            f"expected {supposed_length} lines, " \
            f"got {self.nb_results}."

        return dict(
            [
                self.tuple_string_to_tuple_object(ins)
                for ins in self.raw_content
            ]
        )
