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
                     help="File containing the DataFrame to analyze.",
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
_parser.add_argument("--savegraph",
                     help="Saves the graph drawn at the end of the processing part. "
                          "Naming convention: <file_name>_<day>_<month>_<year>_graph.png "
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
                          "Must be a user name (not a uid). "
                          "e.g. root",
                     type=str, nargs=1)
_parser.add_argument("--savebyext",
                     help="Saves a DataFrame containing only the files "
                          "which have the specified extension. "
                          "Must be an extension, without leading dot. "
                          "e.g. csv",
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

if _args.savegraph:
    _save_graph = True
    now = datetime.now()
    _graph_path = Path('.').resolve() / f'{_file}_{now.day}_{now.month}_{now.year}_graph.png'
else:
    _save_graph = False
    _graph_path = None

if _args.computeonly:
    _compute_only = True
else:
    _compute_only = False

if _args.savebyuser:
    _save_by_user = True
    _user_name = _args.savebyuser[0]
else:
    _save_by_user = False
    _user_name = None

if _args.savebyext:
    _save_by_ext = True
    _ext = _args.savebyext[0]
else:
    _save_by_ext = False
    _ext = None


if __name__ == "__main__":

    print(f'Launched on {datetime.now()}')

    if _compute_only and not _save:
        warn('`--save` was not indicated, but mandatory when passing `--computeonly`. '
             'Switching `--save` from False to True.')
        _save = True
        if _save_graph:
            warn('`--savegraph` was indicated, but is incompatible with `--computeonly`. '
                 'Switching `--savegraph` from True to False.')

    analyzer = ftd.Analyzer(_file, _load, _save)

    if _save_by_user:
        analyzer.save_df_by_user(_user_name)

    if _save_by_ext:
        analyzer.save_df_by_ext(_ext)

    if not _compute_only:
        dashboard = ftd.Dashboard(analyzer)
        dashboard.dashboard(_save_graph, _graph_path)
