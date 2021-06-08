import argparse

from pathlib import Path
from warnings import warn
from datetime import datetime

import ftd


_parser = argparse.ArgumentParser(
    "Run analytics on a DataFrame generated and post-processed by FTD, "
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
                          "It is strongly advised to save once and load afterwards, "
                          "as the computation can be really expensive."
                          "False by default, specify for True.",
                     action="store_true")
_parser.add_argument("--computeonly",
                     help="If you wish to only compute the stats "
                          "and save them for later visualization, "
                          "no graph will be displayed. "
                          "`--save` is mandatory. "
                          "False by default, specify for True.",
                     action="store_true")
_parser.add_argument("--savebyuser",
                     help="Saves a DataFrame containing only the files "
                          "that are owned by the specified user. "
                          "Can either be an uid or the readable name of the user."
                          "False by default, specify for True.",
                     type=str, nargs=1)

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

if _args.computeonly:
    _compute_only = True
else:
    _compute_only = False

if _args.savebyuser:
    _save_by_user = True
    _user_id = _args.savebyuser[0]
else:
    _save_by_user = False
    _user_id = None


if __name__ == "__main__":

    print(f'Launched on {datetime.now()}')

    if _compute_only and not _save:
        warn('`--save` was not indicated, but mandatory when passing `--computeonly`. '
             'Switching `--save` from False to True.')
        _save = True

    analyzer = ftd.Analyzer(_file, _load, _save)

    if _save_by_user:
        analyzer.save_df_by_user(_user_id)

    if not _compute_only:
        dashboard = ftd.Dashboard(analyzer)
        dashboard.dashboard()
