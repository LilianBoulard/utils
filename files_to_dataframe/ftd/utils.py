import pandas as pd

from time import time
from pathlib import Path
from typing import List

from .config import parquet_write_kwargs, parquet_read_kwargs


def get_lists_intersection(list1: List[int], list2: List[int]):
    return list(set(list1) & set(list2))


def log_duration(message):
    """
    A decorator that can be used to print information regarding the execution duration of a function.
    """
    def decorator(func):
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
