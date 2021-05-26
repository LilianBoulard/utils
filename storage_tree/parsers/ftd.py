import os
import pandas as pd

from .base import BaseParser
from typing import List, Tuple


class Parser(BaseParser):

    """
    Used to parse the output of files_to_dataframe.
    Example of expected input:

    ```
    df = pandas.DataFrame(
    {
        'path': [
            '/path/to/file1',
            '/path/to/file2',
            '/path/to/file3'
        ],
        'size': [
            1024,
            10241024,
            102410241024
        ]
    })
    ```

    """

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

    def _read_file(self) -> pd.DataFrame:
        return pd.read_parquet(self.file, engine='fastparquet')

    def _get_content(self) -> List[Tuple[str, int]]:
        paths = list(self.raw_content.to_dict().values())[0].values()
        sizes = list(self.raw_content.to_dict().values())[1].values()
        results = list(zip(paths, sizes))
        return results

    def _get_root(self) -> str:
        return self.content[0][0].split(os.sep)[0]
