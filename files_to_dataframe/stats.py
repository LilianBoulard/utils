import argparse
import pandas as pd

from pathlib import Path
from datetime import datetime

import ftd
from ftd import _utils


_utils.tune_matplotlib_backend()


_parser = argparse.ArgumentParser(
    "Run analytics on a DataFrame generated and post-processed by FTD, "
    "and display a dashboard containing useful information."
)

_parser.add_argument("-f", "--file",
                     help="File containing the DataFrame to analyze.",
                     type=str, nargs=1, required=True)
_parser.add_argument("--savegraph",
                     help="Saves the graph drawn at the end of the processing part. "
                          "Naming convention: <file_name>_<day>_<month>_<year>_graph.png "
                          "False by default, specify for True.",
                     action="store_true")

_args = _parser.parse_args()

_file = Path(_args.file[0]).resolve()

if _args.savegraph:
    _save_graph = True
    now = datetime.now()
    _graph_path = Path('.').resolve() / f'{_file}_{now.day}_{now.month}_{now.year}_graph.png'
else:
    _save_graph = False
    _graph_path = None


def main():
    print(f'Launched on {datetime.now()}')

    dashboard = ftd.Dashboard(pd.read_parquet(_file))
    dashboard.dashboard(_save_graph, _graph_path)


if __name__ == "__main__":
    main()
