import pandas as pd

from typing import Dict, List, Union

from .base import BaseManipulator


class ByUserManipulator(BaseManipulator):

    """
    Structure:
    {
        'indices': {
            'username': List[int],
            ...
        },
        'sizes': {
            'username': int,
            ...
        }
    }
    """

    ManipulatorContentType = Dict[str, Dict[str, Union[int, List[int]]]]

    USERNAME_COLUMN_NAME = 'username'
    USER_ID_COLUMN_NAME = 'uid'
    SIZES_COLUMN_NAME = 'size'

    def _get_usage_by_user(self) -> ManipulatorContentType:
        """
        Returns a dictionary with as key the username,
        and as value the total space "used" by that user in bytes
        (computed via file ownership).
        """
        return {
            user: self.collection.size_manipulator.get_sum_by_index(indices)
            for user, indices in self.content['indices'].items()
        }

    def sort(self) -> None:
        """
        Sorts the content so that the first value is the user that uses the most space,
        and the last item the user that uses the least.
        """
        self.content['sizes'] = dict(
            sorted(
                self.content['sizes'].items(),
                key=lambda pair: pair[1],
                reverse=True
            )
        )

    def init_iter_df(self, df: pd.DataFrame) -> None:
        self.content = {
            'indices': {uname: [] for uname in df['username'].unique()}
        }

    def process_row(self, idx: int, **kwargs) -> None:
        self.content['indices'][kwargs['username']].append(idx)

    def post_process(self) -> None:
        self.content.update({'sizes': self._get_usage_by_user()})
        self.sort()
