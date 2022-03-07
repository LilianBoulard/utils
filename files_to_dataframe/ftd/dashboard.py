import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from typing import List
from pathlib import Path

from .analyzer import Analyzer
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

    def __init__(self, analyzer: Analyzer):
        self._analyzer = analyzer
        self.displayed_users: List[str] = []
        self.displayed_extensions: List[str] = []

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
            # Cast the size to the best possible "size bound"
            # (idk how to say that)
            # e.g. if a file is 20 000 bytes, cast to ~20KB
            for s in self._size_mapping:
                if absolute < 1024:
                    size = s
                    break
                else:
                    absolute /= 1024
            else:
                size = self._size_mapping[-1]
            return "{:.1f}{}\n{:.1f}%".format(absolute, size, percentage)

        if standalone:
            fig, ax = plt.figure(8, 9)

        user_content = self._analyzer.manipulators.user_manipulator.get_content()['sizes']
        counts = list(user_content.values())[:n_users]
        users = list(user_content.keys())[:n_users]
        remaining_counts = list(user_content.values())[n_users:]
        remainder = 0
        # Rename empty username
        if '' in users:
            users[users.index('')] = 'Nobody'

        self.displayed_users = users.copy()

        # Congregate remaining counts and users, and add it to the list.
        sum_remaining_counts = sum(remaining_counts)
        if sum_remaining_counts > 0:
            counts.append(sum_remaining_counts)
            users.append('Other users')
            remainder = 1

        ax.pie(counts, labels=users, startangle=140,
               autopct=lambda pct: format_pct(pct, counts))
        ax.set_title(f'Top {len(users) - remainder} users')

        if standalone:
            plt.show()

    def _extension_by_time_stacked_bar(self, ax=None, standalone: bool = True, n_ext: int = 8) -> None:
        """
        Displays an histogram which shows the `n` extensions that uses the most space,
        split among different time ranges (defined by `ftd.manipulators.ByDateManipulator._ranges`).

        :param int n_ext: The number of extensions to show at most.
        """

        if standalone:
            fig, ax = plt.figure(8, 9)

        date_content = self._analyzer.manipulators.date_manipulator.get_content()
        ext_content = self._analyzer.manipulators.ext_manipulator.get_content()

        # Get the `n` heaviest extensions.
        top_ext = list(ext_content['sizes'].keys())[:n_ext]

        self.displayed_extensions = top_ext.copy()

        data = {}
        for range_name, indices in tuple(date_content['atime'].items())[::-1]:
            sizes = self._analyzer.get_sizes_by_ext_and_index(top_ext, indices)
            # Convert to GB
            sizes = [size / (1024 ** 3) for size in sizes]
            data.update({range_name: sizes})

        # Rename empty extension
        if '' in top_ext:
            top_ext[top_ext.index('')] = 'No extension'

        # TODO: Format the extensions to show a little more information
        # (namely percentage and total usage)
        labels = top_ext

        df = pd.DataFrame(data, index=labels)
        df.plot(ax=ax, kind='bar', rot=25, stacked=True)

        ax.set_ylabel('Size in GB')
        ax.set_title(f'Disk usage by extension, filtered by last access')

        if standalone:
            plt.show()

    def _extension_by_user_stacked_bar(self, ax=None, standalone: bool = True) -> None:

        if standalone:
            fig, ax = plt.figure(8, 9)

        user_content = self._analyzer.manipulators.user_manipulator.get_content()
        extensions = self.displayed_extensions

        data = {}
        for user_name in self.displayed_users:
            user_id = user_name if user_name != 'Nobody' else ''
            user_indices = user_content['indices'][user_id]
            sizes = self._analyzer.get_sizes_by_ext_and_index(
                extensions,
                user_indices
            )
            # Convert to GB
            sizes = [size / (1024 ** 3) for size in sizes]
            data.update({user_name: sizes})

        # Rename empty extension
        if '' in extensions:
            extensions[extensions.index('')] = 'No extension'

        df = pd.DataFrame(data, index=extensions)
        df.plot(ax=ax, kind='bar', rot=20)

        ax.set_ylabel('Size in GB')
        ax.set_title('Usage per extension / user')

        if standalone:
            plt.show()

    def _usage_by_directory_stacked_bar(self, ax=None, standalone: bool = True, n_dir: int = 8) -> None:
        """
        Display a stacked bar plot showing
        which users use the most space by subdirectory at a given depth.

        :param int n_dir: The number of directories to show at most.
        """

        if standalone:
            fig, ax = plt.figure(8, 9)

        dir_content = self._analyzer.manipulators.dir_manipulator.get_content()

        top_dirs = list(dir_content['sizes'].keys())[:n_dir]

        data = {}
        for user_name in self.displayed_users:
            user_id = user_name if user_name != 'Nobody' else ''
            user_indices = self._analyzer.manipulators.user_manipulator.content['indices'][user_id]
            sizes = self._analyzer.get_directory_usage_by_index(top_dirs, user_indices)
            # Convert to GB
            sizes = [size / (1024 ** 3) for size in sizes]
            data.update({user_name: sizes})

        df = pd.DataFrame(data, index=top_dirs)
        df.plot(ax=ax, kind='bar', rot=20)

        ax.set_ylabel('Size in GB')
        ax.set_title('Usage per directory')

        if standalone:
            plt.show()
