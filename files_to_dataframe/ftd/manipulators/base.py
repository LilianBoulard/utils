import pickle
import pandas as pd

from abc import ABC
from pathlib import Path

from ..utils import log_duration


class BaseManipulator(ABC):

    """
    file_path: Path
        Path to the file that contains the DataFrame.
        Only used for naming, argument could be removed.

    df: pandas.DataFrame
        DataFrame to analyze.

    load: bool
        Whether we should load the content of a previous execution.

    save: bool
        Whether we should save the content of this execution,
        so that we can load it later on.
    """

    # Overwrite the following values in your class

    # Type hinting of the type of the content.
    # Use builtins and/or `typing` library.
    ManipulatorContentType = None

    def __init__(self, file_path: Path, df: pd.DataFrame, load: bool = False, save: bool = False):
        self.file_path = file_path
        self.df = df
        self._load = load
        self._save = save

        self.PERSISTENT_FILE = (Path('./persistent/') / Path(self.__class__.__name__ + '.pickle')).resolve()

        self.PERSISTENT_FILE.parent.mkdir(exist_ok=True)

        if load:
            self.content = self.load()
        else:
            self.content = self._compute()
            self.sort()

        if save and not load:
            self.save()

    @log_duration('Loading content')
    def load(self) -> ManipulatorContentType:
        """
        From a file on the disk, load the previously computed content.
        """
        with open(self.PERSISTENT_FILE, 'rb') as fl:
            return pickle.load(fl)

    @log_duration('Saving content')
    def save(self) -> None:
        """
        Takes `self.content`, and writes it in a file.
        """
        with open(self.PERSISTENT_FILE, 'wb') as fl:
            pickle.dump(self.content, fl)
        return

    def get_content(self) -> ManipulatorContentType:
        """
        Getter for the content of the manipulator.
        This function should be called after instantiating it
        to get the results.
        """
        return self.content

    def _compute(self) -> ManipulatorContentType:
        """
        Runs the desired manipulator computation,
        and returns the usable content.

        To get the results after the manipulator's instantiation,
        use `get_content()`.
        """
        raise NotImplementedError

    @log_duration('Sorting content')
    def sort(self) -> None:
        """
        Optional. Sorts `self.content` if necessary.
        """
        raise NotImplementedError
