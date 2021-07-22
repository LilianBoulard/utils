import pandas as pd

from time import time
from typing import Dict, List

from .base import BaseManipulator


class ByDateManipulator(BaseManipulator):

    """
    The structure contains first the two columns we're interested in,
    namely `atime` and `mtime`.
    Next, for each range defined in `_range`, we will compute a list of integers,
    which are indices that correlate to the lines of the DataFrame.

    self.content = {
        'atime':
        {
            'range_name': List[int],
            ...
        }
    }
    """

    ManipulatorContentType = Dict[str, Dict[str, List[int]]]

    LAST_ACCESS_COLUMN_NAME = 'atime'
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

    def init_iter_df(self, df: pd.DataFrame) -> None:
        self.content = {'atime': {}}
        self._ranges_: Dict[str, range] = {}

        offset = int(time())
        for name, duration in self._ranges.items():
            t1 = offset
            t0 = 0 if duration == 0 else t1 - duration

            self.content['atime'].update({name: []})
            self._ranges_.update({name: range(t0, t1)})

            # Move offset
            offset = t0

    def process_row(self, idx: int, **kwargs) -> None:
        for range_name, rng in self._ranges_.items():
            if kwargs['atime'] in rng:
                self.content['atime'][range_name].append(idx)
                break

    def post_process(self) -> None:
        self.sort()
