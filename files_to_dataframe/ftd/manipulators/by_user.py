import numpy as np

from typing import Dict

from .base import BaseManipulator
from ..utils import log_duration


class ByUserManipulator(BaseManipulator):

    ManipulatorContentType = Dict[str, int]

    USERNAME_COLUMN_NAME = 'username'
    USER_ID_COLUMN_NAME = 'uid'
    SIZES_COLUMN_NAME = 'size'

    def _get_all_usernames(self) -> np.array:
        """
        Queries the DataFrame, and returns all the unique extensions found.
        """
        return self.df[self.USERNAME_COLUMN_NAME].unique()

    def _get_usage_by_user(self) -> ManipulatorContentType:
        """
        Returns a dictionary with as key the username,
        and as value the total space "used" by that user in bytes
        (computed via file ownership).
        """
        # Init the dictionary
        all_users = {uname: [] for uname in self._get_all_usernames()}
        # Iter over the rows, adding the index on the fly.
        for index, row in self.df.iterrows():
            all_users[row[self.USERNAME_COLUMN_NAME]].append(index)
        return all_users

    @log_duration('Getting indices by user')
    def _compute(self) -> ManipulatorContentType:
        return self._get_usage_by_user()

    def sort(self) -> None:
        """
        Sorts the content so that the first value is the user that uses the most space,
        and the last item the user that uses the least.
        """
        self.content = dict(
            sorted(
                self.content.items(),
                key=lambda pair: pair[1],
                reverse=True
            )
        )
