import pandas as pd

from pathlib import Path
from typing import Dict, List

from .base import BaseManipulator
from ..utils import log_duration, get_lists_intersection


class ByDirectoryManipulator(BaseManipulator):

    ManipulatorContentType = Dict[str, dict]

    PATH_COLUMN_NAME = 'path'
    SIZE_COLUMN_NAME = 'size'
    DEPTH = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init _indices
        self._indices: Dict[str, List[int]]  # Type hinting
        if self._load:
            self._indices = self.content['indices']
        else:
            self._indices = {}

    @log_duration('Getting indices by directory')
    def _get_indices_by_directory(self) -> Dict[str, List[int]]:
        indices_per_dir = {}
        for index, row in self.df.iterrows():
            path = Path(row[self.PATH_COLUMN_NAME])
            # We put -3 below because:
            # (1) we remove one from the length,
            # as it is 1-indexed but indices are 0-indexed.
            # (2) we skip the system root (e.g. '/', 'C:')
            # (3) we skip the directory root we were analyzing
            # Note: TODO: (3) is kinda hard-coded: if analyzing a
            # directory higher in the hierarchy, it will cause errors.
            parent_index = (len(path.parts) - 3) - self.DEPTH
            try:
                parent = path.parents[parent_index]
            except IndexError:
                # It's a file that's above the depth, we'll skip it.
                continue

            parent = str(parent)

            # If the directory does not exist already, add it.
            if parent not in indices_per_dir.keys():
                indices_per_dir[parent] = []

            indices_per_dir[parent].append(index)

        return indices_per_dir

    @log_duration('Getting size by directory')
    def _get_size_by_directory(self) -> Dict[str, int]:
        return {
            path: self._get_size_by_index(pd.Int64Index(indices))
            for path, indices in self._indices.items()
        }

    def _compute(self) -> ManipulatorContentType:
        self._indices = self._get_indices_by_directory()
        return {
            'indices': self._indices,
            'sizes': self._get_size_by_directory()
        }

    @log_duration('Sorting by directory results')
    def sort(self) -> None:
        self.content['sizes'] = dict(
            sorted(
                self.content['sizes'].items(),
                key=lambda pair: pair[1],
                reverse=True
            )
        )

    def _get_size_by_index(self, index: pd.Index) -> int:
        return self.df[self.SIZE_COLUMN_NAME].iloc[index].sum()

    def get_directory_usage_by_index(self, path_list: List[str], indices: List[int]) -> List[int]:
        data = []
        for path in path_list:
            ext_indices = self.content['indices'][path]
            # Note: we don't use `pandas.Index.intersection()`
            # because it is extremely inefficient.
            # One possible optimization would be to use numpy.intersect1d,
            # but might not be worth it because of the array casting.
            inter = get_lists_intersection(indices, ext_indices)
            idx = pd.Index(inter)
            size = self._get_size_by_index(idx)
            data.append(size)
        return data
