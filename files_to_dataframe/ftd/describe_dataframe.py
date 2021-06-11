import argparse
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


parser = argparse.ArgumentParser(
    "Used to gain some insight on a DataFrame's content."
)

parser.add_argument("-f", "--file",
                    help="Path to the file that contains "
                         "the serialized DataFrame.",
                    type=str, nargs=1, required=True)

args = parser.parse_args()

file = args.file[0]


def read_df(file_path: str) -> pd.DataFrame:
    return pd.read_parquet(file_path, engine='fastparquet')


def describe(df: pd.DataFrame):
    print(f'{df.describe()=}')
    print(f'{df.head()=}')
    print(f'{df.nunique()=}')


if __name__ == "__main__":
    describe(read_df(file))
