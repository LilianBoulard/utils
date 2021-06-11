import numpy as np
import pandas as pd

from pathlib import Path
from typing import Dict, List

from .base import BaseManipulator
from ..utils import log_duration, write_dataframe, get_lists_intersection


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
    SIZE_COLUMN_NAME = 'size'

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

    @log_duration('Sorting extensions results')
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

    def _get_all_extensions(self) -> np.array:
        """
        Queries the DataFrame, and returns all the unique extensions found.
        """
        return self.df[self.EXTENSION_COLUMN_NAME].unique()

    @log_duration('Getting indices by extension')
    def _get_all_extensions_indices(self) -> Dict[str, List[int]]:
        # Init the dictionary
        all_ext = {ext: [] for ext in self._get_all_extensions()}
        # Iter over the rows, adding the index on the fly.
        for index, row in self.df.iterrows():
            all_ext[row[self.EXTENSION_COLUMN_NAME]].append(index)
        return all_ext

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
        return self.df[self.SIZE_COLUMN_NAME].iloc[index].sum()

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

    def get_sizes_by_ext_and_index(self, ext_list: List[str], indices: List[int]) -> List[int]:
        data = []
        for ext in ext_list:
            ext_indices = self.content['indices'][ext]
            # Note: we don't use `pandas.Index.intersection()`
            # because it is extremely inefficient.
            # One possible optimization would be to use numpy.intersect1d,
            # but might not be worth it because of the array casting.
            inter = get_lists_intersection(indices, ext_indices)
            idx = pd.Index(inter)
            size = self._get_size_by_index(idx)
            data.append(size)
        return data

    def save_df_by_ext(self, keep_ext: str) -> None:
        """
        Takes the default DataFrame, filters out all the extensions we're not interested in,
        and outputs in the a file, which can then be used for instance with a `storage tree`,
        to figure out where files are by extension.
        """
        write_dataframe(Path(f'df_only_{keep_ext}.df'), self.df.iloc[self._indices[keep_ext]])
