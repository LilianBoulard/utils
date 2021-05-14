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

    # Files under this size (in bytes) will not be registered.
    file_size_threshold = 1024

    def __init__(self, directory: str, mem_limit: int):
        self.directory = directory
        self.mem_limit = mem_limit

        # Temporary directory in which we will store the
        # temporary dataframes to limit memory usage.
        self.temp_dir = os.path.join(os.getcwd(), 'ftd_temp')
        os.mkdir(self.temp_dir)  # If this raises FileExistsError, delete temp dir

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

    def _write_temp_df(self, data: dict) -> None:
        """
        Write a new temporary dataframe.
        """
        index = len(os.listdir(self.temp_dir))
        path = os.path.join(self.temp_dir, f'{index}.tmpdf')
        df = pd.DataFrame.from_dict(data)
        df.to_parquet(path)
        del index, path, df

    def _walk(self) -> None:
        """
        Walk `directory` recursively,
        and store the results in temporary files on the disk.
        """
        info = {'path': [], 'size': []}
        for subdir, dirs, files in os.walk(self.directory):
            current_usage, _ = tracemalloc.get_traced_memory()
            if current_usage > self.mem_limit:
                # If we reached the memory limit,
                # cast the dictionary to a DataFrame and reset the former,
                # freeing some space.
                self._write_temp_df(info)
                del info
                info = {'path': [], 'size': []}
            for file in files:
                file_path = os.path.join(subdir, file)
                try:
                    file_size = os.path.getsize(file_path)
                except (PermissionError, FileNotFoundError, OSError):
                    continue

                if file_size > self.file_size_threshold:
                    info['path'].append(file_path)
                    info['size'].append(file_size)
                del file_size, file_path

        del subdir, dirs, files

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
            new_df = pd.read_parquet(path)
            dataframes.append(new_df)
            os.remove(path)
        del path, new_df
        # Finally, remove the temp directory
        os.rmdir(self.temp_dir)
        # And concatenate all the dataframes
        df = pd.concat(objs=dataframes)
        del dataframes
        return df

    def store_final_df(self, df: pd.DataFrame) -> None:
        # Requires pyarrow or fastparquet, install with pip
        path = self.clean_path(self.directory) + '_persistent.df'
        df.to_parquet(path)

    def run(self):
        tracemalloc.start()
        t0 = time()

        self._walk()

        df = self._df_from_temp()

        # Get stats
        current, peak = tracemalloc.get_traced_memory()
        parsing_time = time() - t0
        memory_usage = df.memory_usage(index=True).sum()

        # Convert memory usages to megabytes
        peak /= (1024 ** 2)
        memory_usage /= (1024 ** 2)

        print(f'rows={df.shape[0]}, duration={parsing_time:.3f}s, '
              f'df_mem={memory_usage:.3f}MB, all_mem={peak:.3f}MB')

        self.store_final_df(df)
        del df

        tracemalloc.stop()


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
