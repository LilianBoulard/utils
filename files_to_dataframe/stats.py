import argparse

from pathlib import Path
from datetime import datetime

import ftd


_parser = argparse.ArgumentParser(
    "Run analytics on a DataFrame, "
    "and display a dashboard containing useful information."
)

_parser.add_argument("-f", "--file",
                     help="Directory to scan recursively. "
                          "Must be an absolute path.",
                     type=str, nargs=1, required=True)
_parser.add_argument("--load",
                     help="Load the content of a previous run. "
                          "Avoids computation if the data hasn't changed "
                          "since last execution. "
                          "False by default, specify for True.",
                     action="store_true")
_parser.add_argument("--save",
                     help="Saves the results after completing the analysis. "
                          "False by default, specify for True.",
                     action="store_true")

_args = _parser.parse_args()

_file = Path(_args.file[0]).resolve()

if _args.load:
    _load = True
else:
    _load = False

if _args.save:
    _save = True
else:
    _save = False

if __name__ == "__main__":

    print(f'Launched on {datetime.now()}')

    dashboard = ftd.Dashboard(_file, _load, _save)
    dashboard.dashboard()
