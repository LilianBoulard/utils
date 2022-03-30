import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from time import time
from pathlib import Path
from typing import Dict, Optional, List
from itertools import product

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

    def __init__(self, df: pd.DataFrame, total_size: Optional[int] = None):
        self.df = df
        self.total_size = total_size

    @log_duration('Displaying dashboard')
    def dashboard(self, save: bool = False, location: Optional[Path] = None) -> None:
        """
        Displays all the graphs in a subplot.
        """
        fig, axes = plt.subplots(2, 2, dpi=120, figsize=(12, 6), constrained_layout=True)
        self._user_pie_chart(axes[0, 0], standalone=False)
        self._extension_by_time_stacked_bar(axes[0, 1], standalone=False)
        self._usage_by_directory_bar_plot(axes[1, 0], standalone=False)
        self._extension_by_user_bar_plot(axes[1, 1], standalone=False)
        if save:
            self._save_graph(location)
            print(f'Saved graph at {location!r}')
        plt.show()

    def _save_graph(self, location: Path) -> None:
        plt.savefig(location)

    def _user_pie_chart(self, ax=None, standalone: bool = True,
                        n_users: int = 5) -> None:
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
        other_size = other.sum()
        displayed_counts.append(other_size)
        displayed_users.append('Other users')

        # Add a free space part to the pie if specified.
        if self.total_size:
            displayed_counts.append(self.total_size - (displayed.sum() + other_size))
            displayed_users.append('Free space')

        print('User pie chart data:')
        print(displayed_users, displayed_counts)
        ax.pie(displayed_counts, labels=displayed_users, startangle=140,
               autopct=lambda pct: format_pct(pct, displayed_counts))
        ax.set_title(f'Top {len(displayed_users)} users')

        if standalone:
            plt.show()

    def _extension_by_time_stacked_bar(self, ax=None, standalone: bool = True,
                                       n_ext: int = 8) -> None:
        """
        Displays an histogram which shows the `n` extensions that uses
        the most space, split among different time ranges.
        """

        if standalone:
            fig, ax = plt.figure(8, 9)

        # Get the extensions that take the most space.
        top_ext = self.df.groupby(['extension'])['size'].sum().sort_values(ascending=False).iloc[:n_ext].index.to_list()

        # Get a sub-df with only the extensions we're not interested in.
        df = self.df[self.df['extension'].isin(top_ext)]

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
            df.loc[:, range_name] = df['atime'].between(lower_bound, upper_bound, inclusive='left')
            # Move offset
            offset = lower_bound

        # "data" will have as index the extensions, as columns the size ranges
        # time range, and as values the total size corresponding.
        data = pd.DataFrame(index=top_ext)
        for range_name, duration in ranges.items():
            sizes = df.groupby(['extension', range_name])['size'].sum()
            sizes = sizes.reset_index(level=[1])
            # If there is at least one True, get the values, otherwise,
            # create a vector of zeroes.
            if sizes[range_name].sum() > 1:
                mask = sizes[range_name]
                sizes = sizes[mask]
                del sizes[range_name]
                # Rename the "size" column before merging it to the data
                sizes = sizes.rename(columns={'size': range_name})
                data = pd.concat([data, sizes[range_name]], axis=1)
            else:
                sizes = [0] * len(top_ext)
                data[range_name] = sizes
        data.fillna(0)

        # Convert sizes to the appropriate unit scale
        # 1. Get the overall max value
        all_max = int(data.max(axis=1).max())
        # 2. Get unit index
        unit_index = len(str(all_max)) // 3
        if len(str(all_max)) % 3 == 0:
            # Avoids having decimal in case we're close to the upper unit.
            unit_index -= 1
        # 3. Apply the standardization on all values
        data = data.applymap(lambda size: size / (1024 ** unit_index))

        # TODO: Rename empty extension

        print('Extension by time data:')
        print(data)
        data.plot(ax=ax, kind='bar', rot=25, stacked=True)

        ax.set_ylabel(f'Size in {self._size_mapping[unit_index]}')
        ax.set_title(f'Disk usage by extension, categorized by last access')

        if standalone:
            plt.show()

    def _usage_by_directory_bar_plot(self, ax=None, standalone: bool = True,
                                     n_dir: int = 8, n_users: int = 5,
                                     depth: Optional[int] = None) -> None:
        """
        Display a bar plot showing which users use the most space by
        subdirectory at a given depth.

        Pass depth if you know it, otherwise, using None, it will be guessed.
        """

        def format_path(path_parts: List[str]):
            if len(path_parts) == 0:
                return '/'
            return f"/{'/'.join(path_parts)}/"

        if standalone:
            fig, ax = plt.figure(8, 9)

        # Get a sub-df with only the users that we're interested in
        all_users = self.df.groupby(['username'])['size'].sum().sort_values(ascending=False)
        top_users = all_users.iloc[:n_users].index.to_list()
        other_users = all_users.iloc[n_users:].index.to_list()

        # Automatically find the depth if not passed.
        # This is done by comparing all the paths together, and finding the
        # first directory which diverges.
        sample_parts = self.df['path'].iloc[0].split('/')
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
                if not self.df['path'].str.startswith(format_path(sample_parts[:i])).all():
                    depth = i - 1
                    break

        # Make a regex with the root directory to catch the subdirectories.
        root_dir = format_path(sample_parts[:depth])
        next_dir_regex = re.compile(rf"{root_dir}([a-zA-Z0-9_\-. ]+/)")
        # Add a column with the subdirectories extracted from the path.
        self.df.loc[:, 'subdir'] = self.df['path'].str.extract(next_dir_regex, expand=False)
        # Get the heaviest directories
        top_dirs = self.df.groupby(['subdir'])['size'].sum().sort_values(ascending=False).iloc[:n_dir].index.to_list()

        data = pd.DataFrame(index=top_users + ['Other users'], columns=top_dirs)
        groups = self.df.groupby(['username', 'subdir'])['size'].sum()
        # Construct data iteratively
        for user, directory in product(top_users, top_dirs):
            if (user, directory) in groups:
                data.loc[user, directory] = groups[user, directory]

        # Add other users' data
        other_df = self.df[self.df['username'].isin(other_users) & self.df['subdir'].isin(top_dirs)]
        other_groups = other_df.groupby(['username', 'subdir'])['size'].sum()
        # Add data iteratively
        for directory in top_dirs:
            if directory in other_groups.index.levels[1]:
                data.loc['Other users', directory] = other_groups[:, directory].sum()

        # TODO: Rename empty users

        # Convert sizes to the appropriate unit scale
        # 1. Get the overall max value
        all_max = int(data.max(axis=1).max())
        # 2. Get unit index
        unit_index = len(str(all_max)) // 3
        if len(str(all_max)) % 3 == 0:
            # Avoids having decimal in case we're close to the upper unit.
            unit_index -= 1
        # 3. Apply the standardization on all values
        data = data.apply(lambda size: size / (1024 ** unit_index))

        # FIXME: quickfix
        data = data.T

        print('Usage per directory data:')
        print(data)
        data.plot(ax=ax, kind='bar', rot=20)

        ax.set_ylabel(f'Size in {self._size_mapping[unit_index]}')
        ax.set_title('Usage per directory')

        if standalone:
            plt.show()

    def _extension_by_user_bar_plot(self, ax=None, standalone: bool = True,
                                    n_ext: int = 8, n_users: int = 5) -> None:

        if standalone:
            fig, ax = plt.figure(8, 9)

        # Get the extensions that take the most space.
        top_ext = self.df.groupby(['extension'])['size'].sum().sort_values(ascending=False).iloc[:n_ext].index.to_list()

        # Get a sub-df with only the extensions we're interested in.
        df = self.df[self.df['extension'].isin(top_ext)]

        all_users = df.groupby(['username'])['size'].sum().sort_values(ascending=False)
        top_users = all_users.index[:n_users].to_list()
        other_users = all_users.index[n_users:].to_list()

        size_by_ext = df.groupby(['username', 'extension'])['size'].sum()
        top_n = size_by_ext[size_by_ext.index.isin(top_users, level=0)]

        data = pd.DataFrame(index=top_users, columns=top_ext)
        # Construct data iteratively
        # FIXME: not very optimized, though pretty fast with few users and dirs
        for user, ext in product(top_users, top_ext):
            if (user, ext) in top_n:
                data.loc[user, ext] = top_n[user, ext]

        # Add other users' data
        other_df = self.df[self.df['username'].isin(other_users) & self.df['extension'].isin(top_ext)]
        other_groups = other_df.groupby(['username', 'extension'])['size'].sum()
        # Add data iteratively
        for ext in top_ext:
            if ext in other_groups.index.levels[1]:
                data.loc['Other users', ext] = other_groups[:, ext].sum()

        # Convert sizes to the appropriate unit scale
        # 1. Get the overall max value
        all_max = int(data.max(axis=1).max())
        # 2. Get unit index
        unit_index = len(str(all_max)) // 3
        if len(str(all_max)) % 3 == 0:
            # Avoids having decimal in case we're close to the upper unit.
            unit_index -= 1
        # 3. Apply the standardization on all values
        data = data.apply(lambda size: size / (1024 ** unit_index))

        # TODO: Rename empty users (which are in the index)
        #  And empty extension (which is in the columns)

        # FIXME: quickfix
        data = data.T

        print('Extension by user data:')
        print(data)
        data.plot(ax=ax, kind='bar', rot=20)

        ax.set_ylabel(f'Size in {self._size_mapping[unit_index]}')
        ax.set_title('Usage per extension / user')

        if standalone:
            plt.show()
