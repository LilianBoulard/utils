"""
Python3 utility used to parse a directory recursively,
and store all files info it finds in a pandas DataFrame,
which is then stored as Apache Parquet.
This file can later be used for disk usage analytics.
"""

import os
import re
import argparse
import tracemalloc
import pandas as pd

from time import time


class FilesToDataFrame:

    def __init__(self, directory: str, mem_limit: int):
        self.directory = directory
        self.mem_limit = mem_limit

        # Temporary directory in which we will store the
        # temporary dataframes to limit memory usage.
        self.temp_dir = os.path.join(os.getcwd(), 'ftd_temp')
        os.mkdir(self.temp_dir)  # If this raises FileExistsError, delete temp dir

        tracemalloc.start()

    @staticmethod
    def clean_path(p: str) -> str:
        p = os.path.abspath(p)
        # Divide parts
        p_parts = p.split(os.sep)
        # Clean parts
        p_parts = [re.sub('[^A-Za-z0-9]+', '', part) for part in p_parts]
        # Remove empties
        p_parts = [part for part in p_parts if part != '']
        # Construct name
        p = '_'.join(p_parts)
        return p

    def _write_temp_df(self, data: list) -> None:
        """
        Write a new temporary dataframe.
        """
        index = len(os.listdir(self.temp_dir))
        path = os.path.join(self.temp_dir, f'{index}.tmpdf')
        pd.DataFrame.from_dict(data).to_parquet(path)

    def _walk(self) -> None:
        """
        Walk `directory` recursively,
        and store the results in temporary files on the disk.
        """
        info = []
        for subdir, dirs, files in os.walk(self.directory):
            current_usage, _ = tracemalloc.get_traced_memory()
            if current_usage > self.mem_limit:
                # If we reached the memory limit,
                # cast the dictionary to a DataFrame and reset the former,
                # freeing some space.
                self._write_temp_df(info)
                info = []
            for file in files:
                file_path = os.path.join(subdir, file)
                try:
                    info.append({
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
                except (PermissionError, FileNotFoundError):
                    continue

        self._write_temp_df(info)

    def _df_from_temp(self) -> pd.DataFrame:
        """
        Reads the temporary directory,
        and returns a DataFrame constructed by the files' content.
        """
        dataframes = []
        # Read the temporary dataframes from the disk,
        # and remove them along the way.
        for stored_df in os.listdir(self.temp_dir):
            path = os.path.join(self.temp_dir, stored_df)
            dataframes.append(pd.read_parquet(path))
            os.remove(path)
        # Finally, remove the temp directory
        os.rmdir(self.temp_dir)
        # And concatenate all the dataframes
        df = pd.concat(objs=dataframes)
        return df

    def store_final_df(self, df: pd.DataFrame) -> None:
        # Requires pyarrow or fastparquet, install with pip
        df.to_parquet(self.clean_path(self.directory) + '_persistent.df')

    def run(self):
        t0 = time()

        self._walk()

        df = self._df_from_temp()

        # Get stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        parsing_time = time() - t0
        memory_usage = df.memory_usage(index=True).sum()

        # Convert memory usages to megabytes
        peak /= (1024 ** 2)
        memory_usage /= (1024 ** 2)

        print(f'rows={df.shape[0]}, duration={parsing_time:.3f}s, '
              f'df_mem={memory_usage:.3f}MB, all_mem={peak:.3f}MB')

        self.store_final_df(df)


###############
# ARGS PARSER #
###############

parser = argparse.ArgumentParser(
    "Python3 utility used to parse a directory recursively, "
    "and store all files info it finds in a pandas DataFrame, "
    "which is then stored as Apache Parquet. "
    "This file can later be used for disk usage analytics."
)

parser.add_argument("-d", "--directory",
                    help="Directory to scan recursively. "
                         "Must be an absolute path.",
                    type=str, nargs=1, required=True)
parser.add_argument("-l", "--limit",
                    help="Memory usage limit, in bytes. "
                         "Default is 2147483648 (2GB)",
                    type=int, nargs=1, required=False)

args = parser.parse_args()

root_directory = args.directory[0]

if args.limit:
    limit = args.limit[0]
else:
    limit = 2 * 1024 * 1024 * 1024


if __name__ == "__main__":
    ftdf = FilesToDataFrame(directory=root_directory, mem_limit=limit)
    ftdf.run()
