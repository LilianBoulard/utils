from abc import ABC
from time import time
from typing import Dict
from pathlib import Path


class BaseParser(ABC):
    """
    A parser is used to process the output of a script that lists files,
    and outputs a standardized output suitable to use with `storage_tree`.

    For more information on the process of creating a new parser,
    please refer to `storage_tree/parsers/README.md`.
    """

    # Type hinting of the raw content structure
    # Overwrite this in your child class.
    ReadFileStructure = None

    def __init__(self, output_file: Path):
        print('Parsing input')
        t = time()

        self.file = output_file
        self.raw_content = self._read_file()
        self.content = self._get_content()
        self._sort_content_alphabetically()
        self.root = self._get_root()

        print(f'Done parsing, took {time() - t:.3f}s')

    def _sort_content_by_size(self) -> None:
        self.content = dict(
            sorted(
                self.content.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

    def _sort_content_alphabetically(self) -> None:
        self.content = dict(
            sorted(
                self.content.items(),
                key=lambda x: str(x[0]),
                reverse=True
            )
        )

    def _read_file(self) -> ReadFileStructure:
        """
        Reads the input file, stored in `self.file`,
        and returns a data structure that will be used in `_get_content()`.
        """
        raise NotImplementedError

    def _get_content(self) -> Dict[Path, int]:
        """
        Processes `raw_content`, and returns a list of tuples,
        which themselves contain (1) the absolute file path,
        and (2) the size of this file in bytes.
        """
        raise NotImplementedError

    def _get_root(self) -> str:
        """
        Gets the directory root.
        For instance, the root is "storage" in "/storage/of/server/".
        """
        for path in self.content.keys():
            # We iter only once for maximum efficiency
            return path.parts[0]
