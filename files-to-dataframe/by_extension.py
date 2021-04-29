"""
Provides tools to analyze the files based on their extension.
"""

import os
import pandas as pd


# Import df
df = pd.read_parquet('persistent.df')

# The DataFrame has two columns:
# 1. path
#   - The full path of the file
# 2. size
#   - The file's size, in bytes


column_name = 'extension'


def get_extension(path) -> str:
    file: str = path.split(os.sep)[-1]

    # Remove the dot at the start of hidden files
    if file.startswith('.'):
        file = file[1:]

    file_parts = file.split('.')
    if len(file_parts) > 1:
        return file_parts[-1].lower()
    # If the file contains no dots, return empty
    return ''


def get_file_count_by_extension(dataframe):
    """
    Returns a dictionary mapping containing as key the extension,
    and as value the total number of files of this type.
    """
    count = {}
    for ext in dataframe[column_name].unique():
        count[ext] = dataframe[dataframe[column_name] == ext].shape[0]
    return count


def get_total_size_by_extension(dataframe):
    """
    Returns a dictionary mapping containing as key the extension,
    and as value the total size this type of file occupies in bytes.
    """
    total_size = {}
    for ext in dataframe[column_name].unique():
        all_files_by_ext = dataframe[dataframe[column_name] == ext]
        total_size[ext] = all_files_by_ext['size'].sum()
    return total_size


if __name__ == '__main__':
    df['extension'] = df['path'].apply(get_extension)
    sizes = get_total_size_by_extension(df)
    sizes = dict(sorted(sizes.items(), key=lambda item: item[1]))
    print(sizes)
