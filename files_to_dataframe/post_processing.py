"""
Script used to extract interesting features from a
DataFrame created by `files_to_dataframe.py`.
"""

import os
import argparse
import pandas as pd


fastparquet_kwargs = {
    'engine': 'fastparquet',
    'compression': 'gzip',
    'row_group_offsets': 5000000
}


def read_df(file_path: str) -> pd.DataFrame:
    print('Reading file')
    return pd.read_parquet(file_path, **fastparquet_kwargs)


def write_df(file_path: str, df: pd.DataFrame) -> None:
    print('Writing file')
    df.to_parquet(file_path, **fastparquet_kwargs)


def extract_extension(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new column, `extension`, which stores the file extension.
    """

    print('Extracting extensions')

    def get_extension(path) -> str:
        file_name: str = path.split(os.sep)[-1]

        # Remove the dot at the start of hidden files
        if file_name.startswith('.'):
            file_name = file_name[1:]

        file_parts = file_name.split('.')
        if len(file_parts) > 1:
            return file_parts[-1].lower()
        # If the file contains no dots, return empty
        return ''

    df['extension'] = df['path'].apply(get_extension)

    return df


def post_processing(df: pd.DataFrame) -> pd.DataFrame:
    df = extract_extension(df)
    return df


parser = argparse.ArgumentParser(
    'Script used to extract interesting features from a '
    'DataFrame created by `files_to_dataframe.py`.'
)

parser.add_argument("-f", "--file",
                    help="Path to the file that contains "
                         "the serialized DataFrame."
                         "Will be overwritten with the new DataFrame.",
                    type=str, nargs=1, required=True)

args = parser.parse_args()

file = args.file[0]


if __name__ == "__main__":
    write_df(file, post_processing(read_df(file)))
