from abc import ABC
from typing import List, Tuple


class BaseParser(ABC):
    """
    A parser is used to process the output of a script that lists files,
    and outputs a standardized output suitable to use with `storage_tree`.
    """

    ReadFileStructure = None

    def __init__(self, output_file: str):
        self.file = output_file
        self.raw_content = self._read_file()
        self.content = self._get_content()
        self._sort_content_by_size()
        self.root = self._get_root()

    def _sort_content_by_size(self) -> None:
        """
        Sorts the content.
        """
        self.content.sort(key=lambda x: x[1], reverse=True)

    def _read_file(self) -> ReadFileStructure:
        """
        Read the input file and returns a data structure that will be used in `_get_content()`.
        """
        raise NotImplementedError

    def _get_content(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    def _get_root(self) -> str:
        """
        Gets the directory root.
        For instance, the root is "storage" in "/storage/of/server/".
        """
        raise NotImplementedError

