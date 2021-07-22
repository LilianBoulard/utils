import pickle
import pandas as pd

from abc import ABC
from pathlib import Path


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

    # Overwrite the following values in your child class

    # Type hinting of the type of the content.
    # Use builtins and/or `typing` library.
    ManipulatorContentType = None

    def __init__(self, parent, file_path: Path, load: bool = False, save: bool = False):
        self.collection = parent
        self.file_path = file_path
        self._load = load
        self._save = save
        self.content = None

        self.PERSISTENT_FILE = (Path('./persistent/') / Path(self.__class__.__name__ + '.pickle')).resolve()

        self.PERSISTENT_FILE.parent.mkdir(exist_ok=True)

    def load(self) -> None:
        """
        From a file on the disk, load the previously computed content.
        """
        with open(self.PERSISTENT_FILE, 'rb') as fl:
            self.content = pickle.load(fl)

    def save(self) -> None:
        """
        Takes `self.content`, and writes it in a file.
        """
        with open(self.PERSISTENT_FILE, 'wb') as fl:
            pickle.dump(self.content, fl)

    def get_content(self) -> ManipulatorContentType:
        """
        Getter for the content of the manipulator.
        This function should be called after instantiating it
        to get the results.
        """
        return self.content

    def sort(self) -> None:
        """
        Optional. Sorts `self.content` if necessary.
        """
        raise NotImplementedError

    def init_iter_df(self, df: pd.DataFrame) -> None:
        """
        Initializes instances variables before the parent analyzer
        begins iterating rows, and calling `process_row`.
        """
        raise NotImplementedError

    def process_row(self, idx: int, **kwargs) -> None:
        """
        Takes the information of one line from the dataframe,
        and performs some analysis on it.
        """
        raise NotImplementedError

    def post_process(self) -> None:
        """
        Performs some post-processing, such as feature extraction.
        Also a good time to sort the results.
        """
        raise NotImplementedError
