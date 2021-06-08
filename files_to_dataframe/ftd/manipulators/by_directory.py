from pathlib import Path
from typing import Dict, List

from .base import BaseManipulator
from ..utils import log_duration


class ByDirectoryManipulator(BaseManipulator):

    ManipulatorContentType = Dict[str, int]

    PATH_COLUMN_NAME = 'path'
    SIZE_COLUMN_NAME = 'size'

    def _list_dirs_at_depth(self, d: int):
        """
        Lists all the directories at depth `d`.
        Depth is 0-indexed.
        For instance, in `/path/to/heavy/file.txt`, depths 0 will find `to`, and depth 1 will find `heavy`.
        """
        parts: List[str] = []
        for path_str in self.df['path'].iterrows():
            path = Path(path_str)
            parent_index = len(path.parts) - (len(path.parts) - d)
            try:
                parts.append(path.parents[parent_index])
            except IndexError:
                # It's a file that's above the depth, we'll skip it.
                continue
        return parts

    def _get_size_by_directory(self, dir_list: List[str]) -> Dict[str, int]:
        size_per_dir = {d: 0 for d in dir_list}
        for row in self.df.iterrows():
            path = row[self.PATH_COLUMN_NAME]
            size = row[self.SIZE_COLUMN_NAME]
            for d in dir_list:
                if path.startswith(d):
                    size_per_dir[d] = size_per_dir[d] + size
        return size_per_dir

    def _compute(self) -> ManipulatorContentType:
        return self._get_size_by_directory(self._list_dirs_at_depth(1))

    @log_duration('Sorting by directory results')
    def sort(self) -> None:
        self.content = dict(
            sorted(
                self.content.items(),
                key=lambda pair: pair[1],
                reverse=True
            )
        )
