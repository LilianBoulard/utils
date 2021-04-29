"""
Parses a directory recursively, and stores all files info it finds in a pandas DataFrame,
which is then stored as Apache Parquet.
"""

import os
import pandas as pd

from time import time

# Directory to parse recursively.
# Should be absolute.
directory: str = os.getcwd()


t0 = time()
info = []
for subdir, dirs, files in os.walk(directory):
    for file in files:
        file_path = os.path.join(subdir, file)
        info.append({'path': file_path, 'size': os.path.getsize(file_path)})

df = pd.DataFrame.from_dict(info)

parsing_time = time() - t0
memory_usage = df.memory_usage(index=True).sum() / 1024 / 1024

print(f'rows={df.shape[0]}, {parsing_time=}s, {memory_usage=}MB')

df.to_parquet('persistent.df')  # Requires pyarrow or fastparquet, install with pip
