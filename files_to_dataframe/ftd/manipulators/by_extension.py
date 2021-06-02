import pandas as pd

from pathlib import Path
from typing import Dict, List

from .base import BaseManipulator
from ..utils import log_duration, write_dataframe


class ByExtensionManipulator(BaseManipulator):

    """
    {
        'indices':
        {
            'ext': List[int],
            ...
        }
        'sizes':
        {
            'ext': int,
            ...
        },
        # 'count':
        # {
        #     'ext': int,
        #     ...
        # }
    }
    """

    ManipulatorContentType = Dict[str, dict]

    EXTENSION_COLUMN_NAME = 'extension'
    SIZES_COLUMN_NAME = 'size'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init _indices
        self._indices: Dict[str, List[int]]  # Type hinting
        if self._load:
            self._indices = self.content['indices']
        else:
            self._indices = {}

    def _compute(self) -> ManipulatorContentType:
        # We're setting the indices as an instance attribute,
        # as we'll use it in other methods to avoid computing
        # the same thing several times.
        self._indices = self._get_all_extensions_indices()
        return {
            'indices': self._indices,
            'sizes': self._get_total_size_by_extension(),
            # 'count': self._get_file_count_by_extension()
        }

    def sort(self) -> None:
        for column, d in self.content.items():
            # We'll skip the indices column
            if column == 'indices':
                continue

            self.content[column] = dict(
                sorted(
                    d.items(),
                    key=lambda pair: pair[1],
                    reverse=True
                )
            )

    def _get_all_extensions(self) -> List[str]:
        """
        Queries the DataFrame, and returns all the unique extensions found.
        """
        return list(self.df[self.EXTENSION_COLUMN_NAME].unique())

    def _get_indices_by_ext(self, ext: str) -> List[int]:
        """
        Queries the DataFrame, and returns a list of indices which correspond
        to the lines where the file has the specified extension.
        """
        return list(self.df[self.df[self.EXTENSION_COLUMN_NAME] == ext].index)

    @log_duration('Getting indices by extension')
    def _get_all_extensions_indices(self) -> Dict[str, List[int]]:
        return {
            ext: self._get_indices_by_ext(ext)
            for ext in self._get_all_extensions()
        }

    @log_duration('Getting count by extension')
    def _get_file_count_by_extension(self) -> Dict[str, int]:
        """
        Returns a dictionary mapping with as key the extension,
        and as value the total number of files of this type.
        """
        return {
            ext: len(indices)
            for ext, indices in self._indices.items()
        }

    def _get_size_by_index(self, index: pd.Index) -> int:
        return self.df.iloc[index][self.SIZES_COLUMN_NAME].sum()

    @log_duration('Getting sizes by extension')
    def _get_total_size_by_extension(self) -> Dict[str, int]:
        """
        Returns a dictionary mapping with as key the extension,
        and as value the total size this type of file occupies in bytes.
        """
        return {
            ext: self._get_size_by_index(pd.Int64Index(indices))
            for ext, indices in self._indices.items()
        }

    def get_sizes_by_ext_and_date(self, ext_list: List[str], date_range_indices: List[int]) -> List[int]:
        date_range_index = pd.Int64Index(date_range_indices)
        data = []
        for ext in ext_list:
            ext_indices = self.content['indices'][ext]
            ext_index = pd.Int64Index(ext_indices)
            inter = ext_index.intersection(date_range_index)
            size = self._get_size_by_index(inter)
            data.append(size)
        return data

    def save_df_by_ext(self, keep_ext: str) -> None:
        """
        Takes the default DataFrame, filters out all the extensions we're not interested in,
        and outputs in the a file, which can then be used for instance with a `storage tree`,
        to figure out where files are by extension.
        """
        write_dataframe(Path(f'df_only_{keep_ext}.df'), self.df.iloc[self._indices[keep_ext]])
