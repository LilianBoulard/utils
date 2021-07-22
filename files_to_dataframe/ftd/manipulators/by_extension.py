import pandas as pd

from typing import Dict, List, Union

from .base import BaseManipulator


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
        }
    }
    """

    ManipulatorContentType = Dict[str, Dict[str, Union[int, List[int]]]]

    EXTENSION_COLUMN_NAME = 'extension'
    SIZE_COLUMN_NAME = 'size'

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

    def _get_total_size_by_extension(self) -> Dict[str, int]:
        """
        Returns a dictionary mapping with as key the extension,
        and as value the total size this type of file occupies in bytes.
        """
        return {
            ext: self.collection.size_manipulator.get_sum_by_index(indices)
            for ext, indices in self.content['indices'].items()
        }

    def init_iter_df(self, df: pd.DataFrame) -> None:
        self.content = {
            'indices': {ext: [] for ext in df[self.EXTENSION_COLUMN_NAME].unique()}
        }

    def process_row(self, idx: int, **kwargs) -> None:
        self.content['indices'][kwargs['extension']].append(idx)

    def post_process(self) -> None:
        self.content.update({'sizes': self._get_total_size_by_extension()})
        self.sort()
