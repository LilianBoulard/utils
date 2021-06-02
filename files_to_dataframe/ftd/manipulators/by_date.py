from time import time
from typing import Dict, List

from .base import BaseManipulator
from ..utils import log_duration


class ByDateManipulator(BaseManipulator):

    """
    The structure contains first the two columns we're interested in,
    namely `atime` and `mtime`.
    Next, for each range defined in `_range`, we will compute a list of integers,
    which are indices that correlate to the lines of the DataFrame.

    {
        'atime':
        {
            'range_name': List[int],
            ...
        },
        # 'mtime':
        # {
        #     'range_name': List[int],
        #     ...
        # }
    }
    """

    ManipulatorContentType = Dict[str, Dict[str, List[int]]]

    LAST_ACCESS_COLUMN_NAME = 'atime'
    LAST_MODIFICATION_COLUMN_NAME = 'mtime'
    EXTENSION_COLUMN_NAME = 'extension'

    _ranges: Dict[str, int] = {
        'Less than 3 months': 60 * 60 * 24 * 30 * 3,
        '3 to 6 months': 60 * 60 * 24 * 30 * 3,
        '6 months +': 0,
    }

    def sort(self) -> None:
        pass

    def _compute(self) -> ManipulatorContentType:
        d = {
            'atime': {},
            # 'mtime': {},
        }

        offset = int(time())
        for name, duration in self._ranges.items():
            t1 = offset
            if duration == 0:
                t0 = 0
            else:
                t0 = t1 - duration

            d['atime'].update({name: self._get_last_access_indices(t0, t1)})
            # d['mtime'].update({name: self._get_last_modification_count_by_ext(t0, t1)})

            # Move offset
            offset = t0

        return d

    def _get_indices_by_col(self, column_name: str, t0: int, t1: int) -> List[int]:
        """
        Queries a column to get the indices of files which timestamp
        in column `column_name` ranges between t0 (inclusive) and t1 (exclusive).

        :param str column_name: The column to query.
        :param int t0: beginning UNIX timestamp
        :param int t1: end UNIX timestamp
        """
        return list(self.df.query(f'{t0} <= {column_name} < {t1}').index)

    @log_duration('Getting last access indices')
    def _get_last_access_indices(self, t0: int, t1: int) -> List[int]:
        return self._get_indices_by_col(self.LAST_ACCESS_COLUMN_NAME, t0, t1)

    @log_duration('Getting last modification indices')
    def _get_last_access_indices(self, t0: int, t1: int) -> List[int]:
        return self._get_indices_by_col(self.LAST_MODIFICATION_COLUMN_NAME, t0, t1)
