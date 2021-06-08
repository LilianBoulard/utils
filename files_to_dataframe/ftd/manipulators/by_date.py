import pandas as pd

from time import time
from typing import Dict

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

    ManipulatorContentType = Dict[str, Dict[str, pd.Index]]

    LAST_ACCESS_COLUMN_NAME = 'atime'
    LAST_MODIFICATION_COLUMN_NAME = 'mtime'
    EXTENSION_COLUMN_NAME = 'extension'

    # Date ranges
    #
    # How it works:
    # Ranges must be ordered from the most recent to the oldest.
    # For each entry, it must contain as key the name of the range,
    # for instance "Less than 3 months", and as value the duration in seconds
    # between the end of the preceding range and the end of this range
    # (otherwise said, the duration that this range spans).
    # Ranges are incremental, meaning the second range
    # starts where the first range ends, and so on.
    # The first range starts _now_ (the present moment).
    # A special case is reserved for `0`, which indicated that the range
    # spans all the way between the end of the preceding range,
    # and January 1st, 1970 (Unix Epoch).
    #
    # If you decide to change these ranges, for them to take effect,
    # you will need to recompute the stats.
    _ranges: Dict[str, int] = {
        'Less than 3 months': 60 * 60 * 24 * 30 * 3,
        '3 to 6 months': 60 * 60 * 24 * 30 * 3,
        '6 months +': 0,
    }

    def sort(self) -> None:
        pass

    @log_duration('Getting dates indices')
    def _compute(self) -> ManipulatorContentType:
        d = {
            'atime': {},
            # 'mtime': {},
        }

        offset = int(time())
        for name, duration in self._ranges.items():
            t1 = offset
            t0 = 0 if duration == 0 else t1 - duration

            d['atime'].update({name: self._get_last_access_indices(t0, t1)})
            # d['mtime'].update({name: self._get_last_modification_indices(t0, t1)})

            # Move offset
            offset = t0

        return d

    def _get_indices_by_col(self, column_name: str, t0: int, t1: int) -> pd.Index:
        """
        Queries a column to get the indices of files which timestamp
        in column `column_name` ranges between t0 (inclusive) and t1 (exclusive).

        :param str column_name: The column to query.
        :param int t0: beginning UNIX timestamp
        :param int t1: end UNIX timestamp
        """
        return self.df.query(f'{t0} <= {column_name} < {t1}').index

    def _get_last_access_indices(self, t0: int, t1: int) -> pd.Index:
        return self._get_indices_by_col(self.LAST_ACCESS_COLUMN_NAME, t0, t1)

    def _get_last_modification_indices(self, t0: int, t1: int) -> pd.Index:
        return self._get_indices_by_col(self.LAST_MODIFICATION_COLUMN_NAME, t0, t1)
