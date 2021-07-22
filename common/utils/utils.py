import os

import pandas as pd

from time import time
from typing import List
from pathlib import Path
from functools import wraps


parquet_write_kwargs = {
    'engine': 'fastparquet',
    'compression': 'gzip',
    'row_group_offsets': 5000000
}

parquet_read_kwargs = {
    'engine': 'fastparquet'
}


def get_lists_intersection(list1: List[int], list2: List[int]):
    return list(set(list1) & set(list2))


def log_duration(message):
    """
    A decorator that can be used to print information regarding the execution duration of a function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(message)
            t0 = time()
            r = func(*args, **kwargs)
            print(f'Took {time() - t0:.3f}s')
            return r
        return wrapper
    return decorator


@log_duration('Reading DataFrame')
def read_dataframe(file_path: Path) -> pd.DataFrame:
    return pd.read_parquet(file_path, **parquet_read_kwargs)


@log_duration('Writing DataFrame')
def write_dataframe(file_path: Path, df: pd.DataFrame) -> None:
    df.to_parquet(file_path, **parquet_write_kwargs)


def tune_matplotlib_backend():
    # Detect if there is no display, and if so, change backend.
    try:
        if os.environ['DISPLAY'] == ':0.0':
            raise KeyError
    except KeyError:
        import matplotlib
        matplotlib.use('Agg')
