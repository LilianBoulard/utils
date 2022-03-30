import argparse

from pathlib import Path
from typing import Optional
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
_parser.add_argument("--totalsize",
                     help="The total size available on the system in bytes "
                          "(applicable to the data passed).",
                     nargs=1, type=int)

_args = _parser.parse_args()

_file = Path(_args.file[0]).resolve()

_graph_path: Optional[Path]
if _args.savegraph:
    _save_graph = True
    now = datetime.now()
    _graph_path = Path('.').resolve() / f'{_file.stem}_{now.day}_{now.month}_{now.year}_graph.png'
else:
    _save_graph = False
    _graph_path = None

_total_size: Optional[int]
if _args.totalsize:
    _total_size = _args.totalsize[0]
else:
    _total_size = None


def main():
    print(f'Launched on {datetime.now()}')

    dashboard = ftd.Dashboard(
        _utils.read_dataframe(_file),
        total_size=_total_size,
    )
    dashboard.dashboard(_save_graph, _graph_path)


if __name__ == "__main__":
    main()
