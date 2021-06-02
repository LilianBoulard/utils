import pandas as pd

from time import time
from pathlib import Path

from .config import parquet_write_kwargs, parquet_read_kwargs


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


def read_dataframe(file_path: Path) -> pd.DataFrame:
    return pd.read_parquet(file_path, **parquet_read_kwargs)


def write_dataframe(file_path: Path, df: pd.DataFrame) -> None:
    df.to_parquet(file_path, **parquet_write_kwargs)
