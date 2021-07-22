import pandas as pd

from typing import Dict, List

from .base import BaseManipulator


class BySizeManipulator(BaseManipulator):

    """

    self.content = {
        'sizes': List[int]
    }

    """

    ManipulatorContentType = Dict[str, List[int]]

    def sort(self) -> None:
        # We won't sort, because it would scramble the indices.
        pass

    def init_iter_df(self, df: pd.DataFrame) -> None:
        self.content = {
            'sizes': []
        }

    def process_row(self, idx: int, **kwargs) -> None:
        self.content['sizes'].append(kwargs['size'])

    def post_process(self) -> None:
        self.sort()

    def get_sizes_by_index(self, index: List[int]) -> List[int]:
        return [self.content['sizes'][i] for i in index]

    def get_sum_by_index(self, index: List[int]) -> int:
        return sum(self.get_sizes_by_index(index))
