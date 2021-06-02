import argparse

from pathlib import Path
from datetime import datetime

import ftd


_parser = argparse.ArgumentParser(
    "Python3 utility used to parse a directory recursively, "
    "and store all files info it finds in a pandas DataFrame, "
    "which is then stored as Apache Parquet. "
    "This file can later be used for disk usage analytics."
)

_parser.add_argument("-d", "--directory",
                     help="Directory to scan recursively. "
                          "Must be an absolute path.",
                     type=str, nargs=1, required=True)
_parser.add_argument("-l", "--limit",
                     help="Memory usage limit, in bytes. "
                          "Default is 2147483648 (2GB).",
                     type=int, nargs=1)
_parser.add_argument("--skipparse",
                     help="Specify to skip parsing. "
                          "If you want to run the post-processing, "
                          "you will need to specify `--file`.",
                     action="store_true")
_parser.add_argument("--skippost",
                     help="Specify to skip post-processing.",
                     action="store_true")
_parser.add_argument("--file",
                     help="Path to the file that contains the DataFrame. "
                          "Only necessary for post-processing if "
                          "`--skipparse` is specified.",
                     type=str, nargs=1)

_args = _parser.parse_args()

_root_directory = Path(_args.directory[0]).resolve()

if _args.limit:
    _mem_limit = _args.limit[0]
else:
    _mem_limit = 2 * 1024 * 1024 * 1024

if _args.skipparse:
    skip_parsing = True
else:
    skip_parsing = False

if _args.skippost:
    skip_post_process = True
else:
    skip_post_process = False


if __name__ == "__main__":

    print(f'Launched on {datetime.now()}')

    if skip_parsing:
        _file = Path(_args.file[0])
    else:
        _file = ftd.FilesToDataFrame(directory=_root_directory, mem_limit=_mem_limit).get_final_df_path()

    if not skip_post_process:
        df = ftd.utils.read_dataframe(_file)
        ftd.PostProcessor(_file, df)
