import os

from pathlib import Path
from argparse import ArgumentParser

import duplicates as du

_parser = ArgumentParser(
    'Utility for parsing a directory, and finding duplicates.'
)

_parser.add_argument(
    '-d', '--directory',
    help='Directory to scan recursively. '
         'Default is current directory',
    type=str, required=True, default=[os.getcwd()], nargs=1,
)
_parser.add_argument(
    '-l', '--memory_limit',
    help='Memory limit for the parser. In bytes. Default is 2147483648 (2GB).',
    type=int, required=False, default=[2147483648],
)
_parser.add_argument(
    '--dashboard',
    help='Creates a dashboard of the data. '
         'Specify a file name to which HTML will be exported.',
    type=str, required=False, nargs=1,
)

_args = _parser.parse_args()

_directory = _args.directory[0]
_limit = _args.memory_limit[0]

if _args.dashboard:
    _generate_dashboard = True
    _dashboard_output_file = Path(_args.dashboard[0]).resolve()
else:
    _generate_dashboard = False
    _dashboard_output_file = None

if __name__ == "__main__":
    parser = du.DuplicateParser(_directory, _limit)

    ext = du.Extractor(parser)
    duplicates = ext.get_duplicates()
    ext.clean_and_overwrite_dataframe()

    df = ext.get_df()

    if _generate_dashboard:
        dashboard = du.Dashboard(df)
        dashboard.generate(output_file=_dashboard_output_file, data=duplicates)

    print('duplicates: ', duplicates)
