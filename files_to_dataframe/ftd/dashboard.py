import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from .manipulators import ByUserManipulator, ByExtensionManipulator, ByDateManipulator

from .utils import read_dataframe


class Dashboard:

    _size_mapping = [
        'B',
        'KB',
        'MB',
        'GB',
        'TB',
        'EB',
    ]

    def __init__(self, file: Path, load: bool = False, save: bool = False):
        self._load = load
        self._save = save

        df = read_dataframe(file)

        self.user_manipulator = ByUserManipulator(file, df, self._load, self._save)
        self.date_manipulator = ByDateManipulator(file, df, self._load, self._save)
        self.ext_manipulator = ByExtensionManipulator(file, df, self._load, self._save)

    def dashboard(self):
        """
        Displays all the graphs in a subplot.
        """
        fig, axes = plt.subplots(1, 2)
        self._user_pie_chart(axes[0], standalone=False)
        self._extension_histogram(axes[1], standalone=False)
        plt.show()

    def _user_pie_chart(self, ax=None, standalone: bool = True, n_users: int = 10) -> None:
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

        user_content = self.user_manipulator.get_content()
        counts = list(user_content.values())[:n_users]
        users = list(user_content.keys())[:n_users]

        ax.pie(counts, labels=users, startangle=140,
               autopct=lambda pct: format_pct(pct, counts))
        ax.set_title(f'Top {len(users)} users')

        if standalone:
            plt.show()

    def _extension_histogram(self, ax=None, standalone: bool = True, n_ext: int = 5) -> None:
        """
        Displays an histogram which shows the `n` extensions that uses the most space,
        split among different time ranges (defined by `ftd.manipulators.ByDateManipulator._ranges`).

        :param ax: Optional. Matplotlib axis. If not passed, use `standalone=True`.
        :param bool standalone: Whether the pie should be displayed in a standalone window.
        :param int n_ext: The number of extensions to show at most.
        """

        if standalone:
            fig, ax = plt.figure(8, 9)

        date_content = self.date_manipulator.get_content()
        ext_content = self.ext_manipulator.get_content()

        # Get the `n` heaviest extensions.
        # They are ordered from the heaviest to the lightest.
        top_ext = list(ext_content['sizes'].keys())[:n_ext]

        # Format the extensions to show a little more information
        # (namely percentage and total usage)
        labels = top_ext

        data = {}
        for range_name, indices in tuple(date_content['atime'].items())[::-1]:
            sizes = self.ext_manipulator.get_sizes_by_ext_and_date(top_ext, indices)
            data.update({range_name: sizes})

        df = pd.DataFrame(data, index=labels)
        df.plot(ax=ax, kind='bar', stacked=True)

        ax.set_title(f'Disk usage by extension, filtered by last access')

        if standalone:
            plt.show()
