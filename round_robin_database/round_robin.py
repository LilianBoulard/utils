import pickle
import tracemalloc

from pathlib import Path
from typing import Any, Tuple


class Cycle:

    """
    Better version of itertools.cycle.
    Well, perhaps not better, but much more comprehensive for sure.
    """

    def __init__(self, iterable):
        self._iterable = iterable
        self._iter_index: int = 0

    def __next__(self):
        # Cycles through indefinitely
        while self._iterable:
            val = self._iterable[self._iter_index]
            self._increment_index()
            yield val

    def __iter__(self):
        return next(self)

    def __getitem__(self, item):
        return self._iterable[item]

    def __setitem__(self, key, value):
        self._iterable[key] = value

    def __len__(self) -> int:
        return len(self._iterable)

    def __str__(self):
        return str(self._iterable)

    def _increment_index(self) -> None:
        self._iter_index = (self._iter_index + 1) % len(self)

    def _decrement_index(self) -> None:
        self_len = len(self)
        if self_len == 0:
            self._iter_index = self_len - 1
        else:
            self._iter_index -= 1

    def append(self, value) -> None:
        """
        Append a new value at the end of the cycle,
        replacing the one at the beginning.
        """
        self._iterable = self._iterable[1:] + value
        self._decrement_index()


class RoundRobin:

    """
    Implements a simple Round-Robin database.

    iterable, default=None
        Any iterable (lists are advised).

    length: int, default=None
        The max number of instances in the database.
        If not passed, `len(iterable)` is used.

    default_value: Any, default=0
        The default value the database will be filled of at initialization.

    file_location: str, default="rr.db"
        Path to the file in which we will store the database.

    """

    def __init__(self, *,
                 iterable=None, length: int = None,
                 default_value: Any = 0,
                 file_location: Path = Path("./rr.db").resolve()):

        self.file_location = file_location

        # Launch memory profiling
        tracemalloc.start()

        if length is not None:
            self.c = Cycle([default_value, ] * length)
            if iterable is not None:
                for v in iterable:
                    self.append(v)
        elif iterable is not None:
            self.c = Cycle([v for v in iterable])
        else:
            raise ValueError('Missing parameter. '
                             'Please pass `length` and/or `iterable`.')

    def __del__(self):
        tracemalloc.stop()

    def __next__(self):
        return next(self.c)

    def __iter__(self):
        return iter(self.c)

    def __getitem__(self, *args, **kwargs):
        return self.c.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.c.__setitem__(*args, **kwargs)

    def __len__(self):
        return len(self.c)

    @classmethod
    def read_from_disk(cls, file_location: Path):
        """
        Reads a file for a Round-Robin database.
        """
        with open(file_location, 'rb') as fl:
            c = pickle.load(fl)

        rr = cls(length=len(c), file_location=file_location)
        rr.c = c
        return rr

    def write_to_disk(self) -> None:
        """
        Takes the current sequence and write it to the disk.
        """
        with open(self.file_location, 'wb') as fl:
            pickle.dump(self.c, fl)

    def append(self, value) -> None:
        """
        Add a new value at the end of the database,
        removing one at its beginning.
        """
        self.c.append([value])

    def get_memory_used(self) -> Tuple[int, int]:
        """
        Gets the memory (in bytes) used.
        Returns (1) the current amount,
        (2) the amount allocated at peak usage.
        """
        current, peak = tracemalloc.get_traced_memory()
        return current, peak
