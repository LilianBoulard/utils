import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from time import time
from pathlib import Path
from typing import Dict, Optional, List

from ._utils import log_duration


class Dashboard:

    _size_mapping = [
        'B',
        'KB',
        'MB',
        'GB',
        'TB',
        'EB',
    ]

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @log_duration('Displaying dashboard')
    def dashboard(self, save: bool = False, location: Path = None) -> None:
        """
        Displays all the graphs in a subplot.
        """
        fig, axes = plt.subplots(2, 2, dpi=120, figsize=(12, 6), constrained_layout=True)
        self._user_pie_chart(axes[0, 0], standalone=False)
        self._extension_by_time_stacked_bar(axes[0, 1], standalone=False)
        self._usage_by_directory_stacked_bar(axes[1, 0], standalone=False)
        self._extension_by_user_stacked_bar(axes[1, 1], standalone=False)
        if save:
            self._save_graph(location)
            print(f'Saved graph at {location!r}')
        plt.show()

    def _save_graph(self, location: Path) -> None:
        plt.savefig(location)

    def _user_pie_chart(self, ax=None, standalone: bool = True, n_users: int = 5) -> None:
        """
        Displays a pie chart showing which `n` users are using the most space (via file ownership).

        :param ax: Optional. Matplotlib axis. If not passed, use `standalone=True`.
        :param bool standalone: Whether the pie should be displayed in a standalone window.
        :param int n_users: The number of users to show at most.
        """

        def format_pct(percentage, all_values):
            absolute = int(percentage / 100. * np.sum(all_values))
            # Cast the size to the best possible size metric
            # e.g. if a file is 20 000 bytes, cast to ~20KB
            for s in self._size_mapping:
                if absolute < 1024:
                    size = s
                    break
                else:
                    absolute /= 1024
            else:
                size = self._size_mapping[-1]
            return f"{absolute:.1f}{size}\n{percentage:.1f}%"

        if standalone:
            fig, ax = plt.figure(8, 9)

        sizes = self.df.groupby(['username'])['size'].sum().sort_values(ascending=False)

        displayed = sizes.iloc[:n_users]
        displayed_counts = displayed.to_list()
        displayed_users = displayed.index.to_list()
        # If an empty user is in the displayed users, replace it by "Nobody"
        # (as in, nobody owns these files).
        if '' in displayed_users:
            displayed_users[displayed_users.index('')] = 'Nobody'

        # Aggregate the data of the other users in a single entry
        other = sizes.iloc[n_users:]
        displayed_counts.append(other.sum())
        displayed_users.append('Other users')

        ax.pie(displayed_counts, labels=displayed_users, startangle=140,
               autopct=lambda pct: format_pct(pct, displayed_counts))
        ax.set_title(f'Top {len(displayed_users)} users')

        if standalone:
            plt.show()

    def _extension_by_time_stacked_bar(self, ax=None, standalone: bool = True, n_ext: int = 8) -> None:
        """
        Displays an histogram which shows the `n` extensions that uses the most space,
        split among different time ranges.
        """

        if standalone:
            fig, ax = plt.figure(8, 9)

        # Get the extensions that take the most space.
        extensions = self.df.groupby(['extension'])['size'].sum().sort_values(ascending=False).iloc[:n_ext].index.to_list()

        # Get a sub-df with only the extensions we're not interested in.
        df = self.df[self.df['extensions'].isin(extensions)]

        # Time ranges. They are mutually exclusive, and must be ordered from
        # the most recent to the oldest.
        ranges: Dict[str, int] = {
            'Less than 3 months': 60 * 60 * 24 * 30 * 3,
            '3 to 6 months': 60 * 60 * 24 * 30 * 3,
            '6 months +': 0,  # Special case, indicating all up to epoch
        }

        # Create a column in the original dataframe for each range,
        # specifying for each line whether the entry is in this range.
        offset = int(time())
        for range_name, duration in ranges.items():
            upper_bound = offset
            lower_bound = 0 if duration == 0 else upper_bound - duration
            df[range_name] = lower_bound < df['atime'] < upper_bound
            # Move offset
            offset = lower_bound

        # The DataFrame will have as lines the extensions, and as columns
        # the time ranges.
        data = pd.DataFrame()
        for range_name, duration in ranges.items():
            sizes = df.groupby(['extension', range_name])['size'].sum().loc[:, True]
            data[range_name] = sizes

        # Convert sizes to the appropriate unit scale
        # 1. Get the overall max value
        all_max = data.max(axis=1).max()
        # 2. Get unit index
        unit_index = len(str(all_max)) // 3
        if all_max % 3 == 0:
            # Avoids having decimal in case we're close to the upper unit.
            unit_index -= 1
        # 3. Apply the standardization on all values
        data = data.applymap(lambda size: size / (1000 ** unit_index))

        # Move the extensions to their own column instead of the index
        data.reset_index(inplace=True)

        # Rename empty extension
        data.loc[data['extension'] == '', 'extension'] = 'No extension'

        data.plot(ax=ax, kind='bar', rot=25, stacked=True)

        ax.set_ylabel(f'Size in {self._size_mapping[unit_index]}')
        ax.set_title(f'Disk usage by extension, filtered by last access')

        if standalone:
            plt.show()

    def _usage_by_directory_stacked_bar(self, ax=None, standalone: bool = True,
                                        n_dir: int = 8, n_users: int = 5,
                                        depth: Optional[int] = None) -> None:
        """
        Display a stacked bar plot showing
        which users use the most space by subdirectory at a given depth.

        Pass depth if you know it, otherwise, using None, it will be guessed.
        """

        def format_path(path_parts: List[str]):
            if len(path_parts) == 0:
                return '/'
            return f"/{'/'.join(path_parts)}/"

        if standalone:
            fig, ax = plt.figure(8, 9)

        # Get a sub-df with only the users that we're interested in
        top_users = self.df.groupby(['user'])['size'].sum().sort_values(ascending=False).iloc[:n_users].index.to_list()
        df = self.df[self.df['user'].isin(top_users)]

        # Automatically find the depth if not passed.
        # This is done by comparing all the paths together, and finding the
        # first directory which diverges.
        sample_parts = df['path'].iloc[0].split('/')
        # Remove the first element from the sample parts, because we assume
        # it is an absolute path, and therefore starts with a slash.
        sample_parts.pop(0)
        if depth is None:
            for i, part in enumerate(sample_parts):
                if i == 0:
                    # Skip if 0, because we assume all the paths are absolute
                    # (testing 0 would be testing if all the paths start
                    # with a slash
                    continue
                if not df['path'].str.startswith(format_path(sample_parts[:i])).all():
                    depth = i
                    break

        # Make a regex with the root directory to catch the subdirectories.
        root_dir = format_path(sample_parts[:depth])
        next_dir_regex = re.compile(rf"{root_dir}([a-zA-Z0-9_\-. ]+/)")
        # Add a column with the sub-directory extracted from the path.
        df['subdir'] = df['path'].str.extract(next_dir_regex)[0]
        # Filter the df again, keeping only the heaviest directories
        top_dirs = df.groupby(['subdir'])['size'].sum().sort_values(ascending=False).iloc[n_dir].index.to_list()
        df = df[df['subdir'].isin(top_dirs)]

        # Now, we only have to group by user and directory, and job done !
        data = df.groupby(['subdirectory', 'user'])['size'].sum()

        # Convert sizes to the appropriate unit scale
        # 1. Get the overall max value
        all_max = data.max(axis=1).max()
        # 2. Get unit index
        unit_index = len(str(all_max)) // 3
        if all_max % 3 == 0:
            # Avoids having decimal in case we're close to the upper unit.
            unit_index -= 1
        # 3. Apply the standardization on all values
        data = data.applymap(lambda size: size / (1000 ** unit_index))

        data.plot(ax=ax, kind='bar', rot=20)

        ax.set_ylabel(f'Size in {self._size_mapping[unit_index]}')
        ax.set_title('Usage per directory')

        if standalone:
            plt.show()

    def _extension_by_user_stacked_bar(self, ax=None, standalone: bool = True,
                                       n_ext: int = 8, n_users: int = 5) -> None:

        if standalone:
            fig, ax = plt.figure(8, 9)

        # Get the extensions that take the most space.
        extensions = self.df.groupby(['extension'])['size'].sum().sort_values(ascending=False).iloc[:n_ext].index.to_list()

        # Get a sub-df with only the extensions we're interested in.
        df = self.df[self.df['extension'].isin(extensions)]

        all_users = df.groupby(['username'])['size'].sum().sort_values(ascending=False)
        top_n_users = all_users.iloc[:n_users]

        size_by_ext = df.groupby(['username', 'extension'])['size'].sum()
        top_n = size_by_ext[size_by_ext.index.isin(top_n_users.index, level=0)]

        # Convert sizes to the appropriate unit scale
        # 1. Get the overall max value
        all_max = top_n.max()
        # 2. Get unit index
        unit_index = len(str(all_max)) // 3
        if all_max % 3 == 0:
            # Avoids having decimal in case we're close to the upper unit.
            unit_index -= 1
        # 3. Apply the standardization on all values
        top_n = top_n.apply(lambda size: size / (1000 ** unit_index))

        # Rename empty extension and empty user
        # TODO

        top_n.plot(ax=ax, kind='bar', rot=20)

        ax.set_ylabel(f'Size in {self._size_mapping[unit_index]}')
        ax.set_title('Usage per extension / user')

        if standalone:
            plt.show()
