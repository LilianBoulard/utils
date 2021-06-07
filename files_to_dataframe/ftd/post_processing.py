"""
Script used to extract interesting features from a
DataFrame created by `files_to_dataframe.py`.
"""

import os
import pandas as pd

from pathlib import Path
from sys import platform

from .utils import log_duration, write_dataframe

# Right now, we use `pwd` for linux,
# which is currently the only distro supported.
try:
    import pwd
except ImportError:
    if platform == 'linux':
        raise ImportError('Please install pwd - pip3 install pwd')
    else:
        from warnings import warn
        warn(
            f'Post-processing is only supported on Linux '
            f'(detected {platform!r})'
        )


class PostProcessor:

    def __init__(self, file: Path, df: pd.DataFrame):
        self.file = file.resolve()
        self.df = df
        self.post_process()
        write_dataframe(file, self.df)

    @staticmethod
    def extract_gz(file_parts: list) -> str:
        """
        Tries to extract the "true" extension of a file with a `gz` extension,
        as it's usually in two parts, e.g. `tar.gz`.
        """
        # If we have at least three parts, e.g. "<file name>.<first_ext_member>.gz"
        if len(file_parts) >= 3:
            # Join the last two parts
            ext = '.'.join(file_parts[-2:])
        else:
            ext = file_parts[-1]
        return ext

    @log_duration('Extracting extensions')
    def extract_extension(self) -> None:
        """
        Creates a new column, `extension`, which stores the file extension.
        """

        def get_extension(path) -> str:
            file_name: str = path.split(os.sep)[-1]

            # Remove the dot at the start of hidden files
            if file_name.startswith('.'):
                file_name = file_name[1:]

            file_parts = file_name.split('.')
            if len(file_parts) > 1:
                ext = file_parts[-1].lower()
                if ext == 'gz':
                    ext = self.extract_gz(file_parts)
                return ext
            # If the file contains no dots, return empty
            return ''

        self.df['extension'] = self.df['path'].apply(get_extension)

    @log_duration('Extracting usernames')
    def extract_usernames_from_uids(self) -> None:
        """
        Creates a new column, `username`, which is exported from `uid`.
        As it queries the system for these usernames, this post-processing step
        must take place on the same computer as the parsing.
        """

        def get_username_by_uid(uid: int) -> str:
            try:
                name = pwd.getpwuid(uid).pw_name
            except KeyError:
                # uid not found
                name = ''
            return name

        unique_uids = list(self.df['uid'].unique())
        # Create a mapping
        mapping = {
            uid: get_username_by_uid(uid)
            for uid in unique_uids
        }
        self.df['username'] = self.df['uid'].map(mapping)

    def post_process(self) -> None:
        """
        Runs the post-processing steps.
        """
        self.extract_extension()
        if platform == 'linux':
            self.extract_usernames_from_uids()
