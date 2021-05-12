import argparse
import pandas as pd


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
    return pd.read_parquet(file_path)


def describe(df: pd.DataFrame):
    print(df.describe())
    print(df.head())


if __name__ == "__main__":
    describe(read_df(file))
