"""
Python3 utility used to parse a directory recursively,
and store all files info in a pandas DataFrame,
which is then stored as Apache Parquet.
"""

import os
import re
import fastparquet  # Only here to raise error if not installed.
import tracemalloc
import pandas as pd

from time import time
from pathlib import Path
from typing import Callable, List, Optional, Any, Dict

from ._utils import write_dataframe, read_dataframe, log_duration


class Parser:

    """
    Efficient parser used to explore very large amounts of data.

    Parameters
    ----------

    directory: Path
        Root directory, will be parsed recursively.

    mem_limit: int, default=2147483648
        Total memory limit in bytes.
        When exceeding this limit, the parser will empty his memory
        by writing the data on the disk. Expect around ~20% overflow.
        Watch out: it counts the total memory used by the Python process,
        so be sure your parent process doesn't take up too much space.

    """

    def __init__(self, directory: Path, mem_limit: int = 2147483648):
        self.directory = directory
        self.mem_limit = mem_limit

    @staticmethod
    def clean_path(p: Path) -> str:
        # Divide parts
        p_parts = str(p).split(os.sep)
        # Clean parts
        p_parts = [re.sub('[^A-Za-z0-9]+', '', part) for part in p_parts]
        # Remove empties
        p_parts = [part for part in p_parts if part != '']
        # Construct name
        p = '_'.join(p_parts)
        return p

    def _write_temp_df(self, data: dict) -> None:
        """
        Write a new temporary dataframe.
        """
        index = len(list(self.temp_dir.iterdir()))
        path = Path(self.temp_dir, f'{index}.tmpdf')
        df = pd.DataFrame.from_dict(data)
        write_dataframe(path, df)

    @log_duration('Walking the root directory')
    def _walk(self,
              structure: List[str],
              file_callback: Optional[Callable] = None,
              directory_callback: Optional[Callable] = None,
              ) -> None:
        """
        Walk `directory` recursively,
        and store the results in temporary files on the disk.
        :param structure: A list of strings, which will be used by the callbacks.
        :param file_callback: The callback which will be called with every file.
        Takes one argument: the file path (string), and returns a dictionary with
        as keys the values of `structure`, representing the columns,
        and as values a single object (any type) which will be appended
        to the column.
        Don't return partial dicts, as it may scramble the line orders.
        :param directory_callback: Same as `file_callback`,
        but takes the directory path instead.
        """
        # Temporary directory in which we will store the
        # temporary dataframes to limit memory usage.
        self.temp_dir = Path.cwd() / 'parser_temp'
        self.temp_dir.mkdir(exist_ok=False)  # If this raises FileExistsError, delete temp dir

        def get_default_dict() -> Dict[str, Any]:
            return {v: [] for v in structure}

        def append_values(new_values: Dict[str, Any], dictionary: Dict[str, Any]):
            for key, value in new_values.items():
                dictionary[key].append(value)

        has_file_callback: bool = file_callback is not None
        has_directory_callback: bool = directory_callback is not None

        info = get_default_dict()
        for root, dirs, files in os.walk(self.directory):
            current_usage, _ = tracemalloc.get_traced_memory()
            if current_usage > self.mem_limit:
                # If we reached the memory limit,
                # cast the dictionary to a DataFrame and write it to disk,
                # and reset the former to free some memory.
                self._write_temp_df(info)
                info = get_default_dict()
            if has_directory_callback:
                append_values(directory_callback(root), info)
            for file in files:
                if has_file_callback:
                    try:
                        append_values(file_callback(os.path.join(root, file)), info)
                    except (FileNotFoundError, OSError, PermissionError):
                        pass

        self._write_temp_df(info)

    def _df_from_temp(self) -> pd.DataFrame:
        """
        Reads the temporary directory,
        and returns a DataFrame constructed by the files' content.
        """
        dataframes = []
        # Read the temporary dataframes from the disk,
        # and remove them along the way.
        for stored_df_path in self.temp_dir.iterdir():
            new_df = read_dataframe(stored_df_path)
            dataframes.append(new_df)
            stored_df_path.unlink()
        # Finally, remove the temp directory
        self.temp_dir.rmdir()
        # And concatenate all the dataframes
        df = pd.concat(objs=dataframes)
        return df

    def get_final_df_path(self) -> Path:
        name = self.clean_path(self.directory) + '_persistent.df'
        return Path('./', name).resolve()

    def store_final_df(self, df: pd.DataFrame, optimization_callback: Optional[Callable] = None) -> None:
        """
        Concatenates all the temporary DataFrames, and stores a final DataFrame on disk.
        :param df: DataFrame to store
        :param optimization_callback: A callback to a function that will be in charge of optimizing the DataFrame.
        It takes one argument: the pandas DataFrame, and returns the optimized pandas DataFrame.
        """
        path = self.get_final_df_path()
        if optimization_callback:
            df = optimization_callback(df)
        write_dataframe(path, df)

    def run(self, *,
            structure: List[str],
            file_callback: Optional[Callable] = None,
            directory_callback: Optional[Callable] = None,
            optimization_callback: Optional[Callable] = None,
            ):
        """
        Main function, runs all the computation.
        For arguments description, see methods `_walk` and `store_final_df`.
        """
        tracemalloc.start()
        t0 = time()

        self._walk(structure, file_callback, directory_callback)
        t1 = time()
        _, walk_peak = tracemalloc.get_traced_memory()
        walk_peak /= (1024 ** 2)
        parsing_time = t1 - t0
        print(f'Parsing stats: '
              f'duration={parsing_time:.3f}s, '
              f'mem_peak={walk_peak:.3f}MB')

        df = self._df_from_temp()
        t2 = time()
        _, pp_peak = tracemalloc.get_traced_memory()
        df_mem_usage = sum(df.memory_usage(index=True))
        pp_peak /= (1024 ** 2)
        df_mem_usage /= (1024 ** 2)
        post_process_time = t2 - t1
        print(f'Post-processing stats: '
              f'duration={post_process_time:.3f}s, '
              f'mem_peak={pp_peak:.3f}MB, '
              f'rows={df.shape[0]}, '
              f'df_mem={df_mem_usage:.3f}MB')

        self.store_final_df(df, optimization_callback)
        t3 = time()
        _, store_peak = tracemalloc.get_traced_memory()
        store_peak /= (1024 ** 2)
        store_time = t3 - t2
        print(f'Storing stats: '
              f'duration={store_time:.3f}s, '
              f'mem_peak={store_peak:.3f}MB')

        _, total_peak = tracemalloc.get_traced_memory()
        total_peak /= (1024 ** 2)
        print(f'Total stats: '
              f'duration={time() - t0:.3f}s, '
              f'peak={total_peak:.3f}MB')

        tracemalloc.stop()
