import numpy as np
import pandas as pd

from typing import Dict, List

from .base import BaseManipulator
from ..utils import log_duration


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

    ManipulatorContentType = Dict[str, dict]

    USERNAME_COLUMN_NAME = 'username'
    USER_ID_COLUMN_NAME = 'uid'
    SIZES_COLUMN_NAME = 'size'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init _indices
        self._indices: Dict[str, List[int]]  # Type hinting
        if self._load:
            self._indices = self.content['indices']
        else:
            self._indices = {}

    def _get_all_usernames(self) -> np.array:
        """
        Queries the DataFrame, and returns all the unique extensions found.
        """
        return self.df[self.USERNAME_COLUMN_NAME].unique()

    @log_duration('Getting indices by user')
    def _get_indices_by_user(self) -> Dict[str, List[int]]:
        all_usernames = self._get_all_usernames()
        # We compute the ratio between the total number of values
        # and the unique values in a column.
        # There is a sweet spot at around 4.5:
        # for a ratio over this threshold,
        # using boolean indexing is more efficient, and under,
        # iterating over the DataFrame and adding
        # the index on the fly is more efficient.
        ratio = self.df.shape[0] / len(all_usernames)
        #if ratio > 4.5:
        # Use boolean indexing
        all_users_indices = {}
        for user in all_usernames:
            all_users_indices[user] = list(self.df[self.df[self.USERNAME_COLUMN_NAME] == user].index)
        #else:
        #    # Use iterrows
        #    # Init the dictionary
        #    all_users_indices = {uname: [] for uname in self._get_all_usernames()}
        #    # Iter over the rows, adding the index on the fly.
        #    for index, row in self.df.iterrows():
        #        all_users_indices[row[self.USERNAME_COLUMN_NAME]].append(index)
        return all_users_indices

    @log_duration('Getting usage by user')
    def _get_usage_by_user(self) -> ManipulatorContentType:
        """
        Returns a dictionary with as key the username,
        and as value the total space "used" by that user in bytes
        (computed via file ownership).
        """
        all_sizes = {}
        for user in self._indices.keys():
            all_sizes[user] = sum(self.df[self.SIZES_COLUMN_NAME].iloc[pd.Index(self._indices[user])])
        return all_sizes

    def _compute(self) -> ManipulatorContentType:
        # We're setting the indices as an instance attribute,
        # as we'll use it in other methods to avoid computing
        # the same thing several times.
        self._indices = self._get_indices_by_user()
        return {
            'indices': self._indices,
            'sizes': self._get_usage_by_user()
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
