from typing import Dict

from .base import BaseManipulator


class ByUserManipulator(BaseManipulator):

    ManipulatorContentType = Dict[str, int]

    USERNAME_COLUMN_NAME = 'username'
    SIZES_COLUMN_NAME = 'size'

    def _get_usage_by_user(self) -> ManipulatorContentType:
        """
        Returns a dictionary with as key the username,
        and as value the total space "used" by that user (in bytes).
        """
        return {
            uname: self.df[self.df[self.USERNAME_COLUMN_NAME] == uname][self.SIZES_COLUMN_NAME].sum()
            for uname in self.df[self.USERNAME_COLUMN_NAME].unique()
        }

    def _compute(self) -> ManipulatorContentType:
        return self._get_usage_by_user()

    def sort(self) -> None:
        """
        Sorts the content so that the first value is the user that uses the most space,
        and the last item the user that uses the least.
        """
        self.content = dict(sorted(self.content.items(), key=lambda pair: pair[1]))
