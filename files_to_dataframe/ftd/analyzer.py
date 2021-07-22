import pandas as pd

from typing import List
from pathlib import Path

from .manipulators.collection import ManipulatorCollection
from ._utils import read_dataframe, write_dataframe, log_duration, get_lists_intersection


class Analyzer:

    """
    The Analyzer contains the instantiated manipulators.
    Note: it will load the dataframe only if needed.
    """

    def __init__(self, file: Path, load: bool = False, save: bool = False):
        self._file = file
        self.load = load
        self.save = save
        self.df = None

        self.manipulators = ManipulatorCollection(
            file_path=file,
            load=self.load,
            save=self.save
        )

        if self.load:
            self._load()
        else:
            self.df = self._load_dataframe()
            self._iter_dataframe()

        if self.save and not self.load:
            self._save()

    def _load_dataframe(self) -> pd.DataFrame:
        return read_dataframe(self._file)

    @log_duration('Loading manipulators from disk')
    def _load(self):
        self.manipulators.call_method('load')

    @log_duration('Saving manipulators to disk')
    def _save(self):
        self.manipulators.call_method('save')

    def _iter_dataframe(self) -> None:
        """
        Takes the DataFrame, and performs a single `iterrows`,
        calling each manipulator's method `process_row` each time.
        """
        @log_duration('Initializing manipulators')
        def _init():
            self.manipulators.call_method('init_iter_df', df=self.df)

        @log_duration("Constructing manipulators' content")
        def _iter():
            i: int
            for i, (path, size, uid, atime, mtime, extension, username) in self.df.iterrows():
                self.manipulators.call_method(
                    'process_row',
                    idx=i,
                    path=path,
                    size=size,
                    uid=uid,
                    atime=atime,
                    mtime=mtime,
                    extension=extension,
                    username=username,
                )

        @log_duration('Post-processing results')
        def _post_process():
            self.manipulators.call_method('post_process')

        _init()
        _iter()
        _post_process()

    # Cross-source stats
    # Methods that use several manipulators to correlate the data.

    @staticmethod
    def _get_index(indices_1: List[int], indices_2: List[int]):
        # Note: we don't use `pandas.Index.intersection()`
        # because it is extremely inefficient.
        # One possible optimization would be to use numpy.intersect1d,
        # but might not be worth it because of the array casting.
        return pd.Index(get_lists_intersection(indices_1, indices_2))

    def get_directory_usage_by_index(self, path_list: List[str], indices: List[int]) -> List[int]:
        """
        Takes a list of directories and a list of indices,
        and returns a list of sizes: the correlation of each directory and the indices.
        TODO: reword docstring
        """
        data = []
        for path in path_list:
            ext_indices = self.manipulators.dir_manipulator.get_content()['indices'][path]
            index = self._get_index(indices, ext_indices)
            size = self.manipulators.size_manipulator.get_sum_by_index(index)
            data.append(size)
        return data

    def get_sizes_by_ext_and_index(self, ext_list: List[str], indices: List[int]) -> List[int]:
        """
        Takes a list of extensions and a list of indices,
        and returns a list of sizes: the correlation of each extension and the indices.
        TODO: reword docstring
        """
        data = []
        for ext in ext_list:
            ext_indices = self.manipulators.ext_manipulator.get_content()['indices'][ext]
            index = self._get_index(indices, ext_indices)
            size = self.manipulators.size_manipulator.get_sum_by_index(index)
            data.append(size)
        return data

    def _save_df_by_index(self, path: Path, indices: List[int]) -> None:
        if not self.df:
            self.df = self._load_dataframe()
        write_dataframe(path, self.df.iloc[indices])

    def save_df_by_ext(self, keep_ext: str) -> None:
        """
        Takes the default DataFrame, filters out all the extensions we're not interested in,
        and outputs in the a file, which can then be used for instance with a `storage tree`,
        to figure out where files are by extension.
        """
        self._save_df_by_index(
            Path(f'df_only_{keep_ext}.df').resolve(),
            self.manipulators.ext_manipulator.get_content()['indices'][keep_ext]
        )

    def save_df_by_user(self, user_identifier: str) -> None:
        self._save_df_by_index(
            Path(f'./ftd_dataframe_of_{user_identifier}.df').resolve(),
            self.manipulators.user_manipulator.get_content()['indices'][user_identifier]
        )
