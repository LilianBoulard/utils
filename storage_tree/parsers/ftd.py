import pandas as pd

from typing import Dict
from pathlib import Path

from .base import BaseParser


class Parser(BaseParser):

    """
    Used to parse the output of files_to_dataframe.
    Example of expected input:

    ```
    pandas.DataFrame(
    {
        'path': [
            '/path/to/file2',
            '/path/to/file1',
            '/path/to/file3'
        ],
        'size': [
            10241024,
            1024,
            102410241024
        ],
        ...
    })
    ```

    """

    ReadFileStructure = pd.DataFrame

    PATHS_COLUMN = 'path'
    SIZES_COLUMN = 'size'

    def _read_file(self) -> ReadFileStructure:
        return pd.read_parquet(self.file, engine='fastparquet')

    def _get_content(self) -> Dict[Path, int]:

        def to_path(path: str) -> Path:
            return Path(path)

        return dict(
            zip(
                self.raw_content[self.PATHS_COLUMN].apply(to_path).to_list(),
                self.raw_content[self.SIZES_COLUMN].to_list()
            )
        )
