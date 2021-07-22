import pandas as pd

from typing import Dict, List

from ._utils import log_duration, write_dataframe


class Extractor:

    def __init__(self, parser):
        self.parser = parser
        self.df = self.parser.get_final_df()
        self.duplicates = None

    @log_duration('Extracting duplicates')
    def get_duplicates(self) -> Dict[str, List[int]]:
        # Init unique values
        vals = {h: [] for h in self.df['hash'].unique()}
        # We'll iterate over each row, and assign the index accordingly
        for i, (path, h) in self.df.iterrows():
            vals[h].append(i)

        self.duplicates = {
            k: v
            for k, v in vals.items()
            if len(v) > 1
        }
        return self.duplicates

    @log_duration('Cleaning DataFrame')
    def clean_and_overwrite_dataframe(self):
        """
        Takes `self.df`, cleans it,
        meaning we remove every line that is not a duplicate of another,
        and we overwrite the one on disk.
        Warning: for the sake of memory consumption,
        `self.df` is directly altered.
        """
        assert self.duplicates

        # TODO: benchmark
        dup_indices = []
        for indices in self.duplicates.values():
            dup_indices.extend(indices)

        df_index = set(self.df.index)
        # Compute the difference
        diff = df_index - set(dup_indices)
        self.df.drop(
            index=diff,
            axis='index',
            inplace=True,
        )

        df_path = self.parser.get_final_df_path()
        write_dataframe(df_path, self.df)

    def get_df(self) -> pd.DataFrame:
        return self.df
