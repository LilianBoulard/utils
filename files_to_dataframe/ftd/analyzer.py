import pandas as pd

from pathlib import Path
from warnings import warn

from .utils import read_dataframe, write_dataframe
from .manipulators import ByUserManipulator, ByExtensionManipulator, ByDateManipulator, ByDirectoryManipulator


class Analyzer:

    def __init__(self, file: Path, load: bool = False, save: bool = False):
        self._file = file
        self._load = load
        self._save = save

        self.df = self.load_dataframe()

        args = (
            file,
            self.df,
            self._load,
            self._save
        )

        self.user_manipulator = ByUserManipulator(*args)
        self.date_manipulator = ByDateManipulator(*args)
        self.ext_manipulator = ByExtensionManipulator(*args)
        self.dir_manipulator = ByDirectoryManipulator(*args)

    def load_dataframe(self) -> pd.DataFrame:
        return read_dataframe(self._file)

    def save_df_by_user(self, user_identifier: str) -> None:
        # First, try casting the identifier to an integer.
        # If that works, we'll assume it's a uid.
        try:
            int(user_identifier)
        except ValueError:
            # If that didn't work, we'll consider it is a username.
            column = self.user_manipulator.USERNAME_COLUMN_NAME
            id_type = 'user name'
        else:
            # We consider it's a uid.
            column = self.user_manipulator.USER_ID_COLUMN_NAME
            id_type = 'uid'

        # Now that we have the type, let's perform the query.
        user_df = self.df[self.df[column] == user_identifier]
        # If the DF contains 0 rows, it means the id is invalid.
        if user_df.shape[0] == 0:
            warn(f'Specified {id_type} {user_identifier!r} is invalid, '
                 f'please verify it is valid.')
            return

        write_dataframe(Path(f'./ftd_dataframe_of_{user_identifier}.df').resolve(), user_df)
