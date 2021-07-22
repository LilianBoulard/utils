import os

import pandas as pd

from typing import Dict
from pathlib import Path

from .base import BaseManipulator


class ByDirectoryManipulator(BaseManipulator):

    ManipulatorContentType = Dict[str, dict]

    SIZE_COLUMN_NAME = 'size'
    DEPTH = 2

    def sort(self) -> None:
        self.content['sizes'] = dict(
            sorted(
                self.content['sizes'].items(),
                key=lambda pair: pair[1],
                reverse=True
            )
        )

    def init_iter_df(self, df: pd.DataFrame) -> None:
        self.content = {
            'indices': {}
        }

    def process_row(self, idx: int, **kwargs) -> None:
        path = kwargs['path']
        path_parts = path.split(os.sep)

        if len(path_parts) <= self.DEPTH + 1:
            return

        parent = os.sep.join(path_parts[:self.DEPTH + 1])

        # If the directory does not exist already, add it.
        if parent not in self.content['indices'].keys():
            self.content['indices'].update({parent: []})

        self.content['indices'][parent].append(idx)

    def _get_size_by_directory(self) -> Dict[str, int]:
        return {
            path: self.collection.size_manipulator.get_sum_by_index(indices)
            for path, indices in self.content['indices'].items()
        }

    def post_process(self) -> None:
        self.content.update({'sizes': self._get_size_by_directory()})
        self.sort()
