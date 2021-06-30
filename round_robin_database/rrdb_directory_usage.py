"""
Round-Robin database used to monitor the usage
of a directory per subdirectories over time.
"""

import os
import argparse

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from math import floor
from pathlib import Path
from statistics import mean
from datetime import datetime
from time import sleep, time, strftime, gmtime
from typing import List, Tuple, Dict, Union, Generator

import round_robin as rr


# Type hint of the structure to store.
# An instance contains a tuple with
# (1) the timestamp of the transaction (UNIX seconds)
# (2) a list of tuples, each containing
# (1) the path (absolute or relative) to the directory
# (2) the size, in bytes, of this directory.
InstanceType = Tuple[int, List[Tuple[Path, int]]]


class DirectoryUsage:

    """
    A Round-Robin database storing the usage of subdirectories of a root dir.
    Useful for visualization of the usage over time.
    """

    default_value = []

    def __init__(self, root: Path, trace: int, delay: int, file_location: Path):
        self.root = root
        self.delay = delay
        self.file_location = file_location

        # Read the database from file if found, otherwise init.
        if file_location.exists():
            print(f'Reading database {file_location!r}')
            self.rr = rr.RoundRobin.read_from_disk(file_location)

        if not file_location.exists() or len(self.rr) != trace:
            print(f'No corresponding database found on disk, '
                  f'creating a new one: {file_location!r}')
            self.rr = rr.RoundRobin(length=trace,
                                    default_value=self.default_value,
                                    file_location=file_location)

        # Dashboard values
        self.fig = None

        self._running: bool = True

    @staticmethod
    def get_directory_size(directory: Union[Path, str]) -> int:
        """
        Recursive function used to get the size of a directory.
        """
        total_size = 0
        for root, subdirs, files in os.walk(directory):
            for f in files:
                fp = os.path.join(root, f)
                # Skip symbolic links
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except (PermissionError, OSError, FileNotFoundError):
                        pass
        return total_size

    def wait(self) -> None:
        sleep(self.delay)

    def is_running(self) -> bool:
        return self._running

    def list_directories(self) -> Generator[Path, None, None]:
        """
        Parses the root and returns the list of directories it contains.
        """
        for path in self.root.iterdir():
            if path.is_dir():
                yield path

    def get_instance(self) -> InstanceType:
        """
        Gets the usage of the root directory,
        and returns an instance ready to be
        inserted into the round-robin database.
        """
        disk_usage = []

        for dir_path in self.list_directories():
            dir_size = self.get_directory_size(dir_path)
            disk_usage.append((dir_path, dir_size))

        timestamp = floor(time())
        return timestamp, disk_usage

    def _run(self, wait: bool = True) -> None:
        """
        Runs the parser once.
        """
        print(f'Parsing {self.root}')
        t = time()
        instance = self.get_instance()
        print(f'Parsed {len(instance[1])} directories')
        self.rr.append(instance)
        print(f'Took {time() - t:.3f}s')

        print('Writing database')
        t = time()
        self.rr.write_to_disk()
        print(f'Took {time() - t:.3f}s')

        if wait:
            print(f'Waiting for {self.delay}s')
            self.wait()

    def run_for(self, num: int) -> None:
        """
        Runs the parser `num` times before stopping.
        """
        for i in range(num):

            # Condition to skip the last wait.
            if i == num - 1:
                wait = False
            else:
                wait = True

            self._run(wait=wait)

    def run_forever(self) -> None:
        """
        Runs the parser indefinitely.
        """
        while self.is_running():
            try:
                self._run()
            except KeyboardInterrupt:
                break

    def dashboard(self, date_format: str = '%a %d %b %Y') -> None:
        """
        Creates a dashboard.

        :param str date_format: Date format to use on the plot.
        See https://docs.python.org/3/library/time.html#time.strftime

        TODO: Cleanup and better handle missing values
        """
        AllType = Dict[str, List[int]]

        def widest_range_plot(tmp_list: List[int], all_ranges: AllType, sub_ax) -> None:
            """
            Draw a plot which contains the widest ranges.
            """
            # Get the appropriate size denominator, e.g. KB, MB, GB...
            max_size: int = max(max(v) for v in all_dirs.values())
            denominator, _ = format_sizes([max_size])
            # Compute the range for each directory
            ranges = {
                dir_name: max(sizes) - min(sizes)
                for dir_name, sizes in all_ranges.items()
            }
            # Sort them
            ranges = dict(sorted(ranges.items(), key=lambda x: x[1], reverse=True))
            # Get total range
            total_range = max(max(v) for v in all_ranges.values()) - \
                          min(min(v) for v in all_ranges.values())
            # For the 10 first (the heaviest)
            top_ranges = list(ranges.items())[:10]
            plotted: int = 0  # To keep track of how many we plotted
            for dir_name, rng in top_ranges:
                # If there is little to no variance, move to the next
                if rng < total_range * 0.05:
                    continue
                # Get the sizes for this directory
                sizes = all_ranges[dir_name]
                # Format them
                _, sizes = format_sizes(sizes, factor=denominator)
                # And plot them
                sub_ax.plot(tmp_list, sizes, label=dir_name)
                plotted += 1
            format_dates(sub_ax)
            sub_ax.set_title(f'Top {plotted} directories with most variance in size')
            sub_ax.set_xlabel("Date")
            sub_ax.set_ylabel(f"Size in {denominator}")
            sub_ax.legend()

        def top_mean_plot(tmp_list: List[int], all_means: AllType, sub_ax) -> None:
            """
            Draw a plot which contains the top means.
            """
            # Get the appropriate size denominator, e.g. KB, MB, GB...
            max_size = max(max(v) for v in all_dirs.values())
            denominator, _ = format_sizes([max_size])
            # Compute the means
            means = {dir_name: mean(sizes) for dir_name, sizes in all_means.items()}
            # Sort them
            means = dict(sorted(means.items(), key=lambda x: x[1], reverse=True))
            # For the 10 first (the heaviest)
            top_means = list(means.items())[:10]
            plotted: int = 0  # To keep track of how many we plotted
            for dir_name, _ in top_means:
                # Get the sizes
                sizes = all_means[dir_name]
                # Format them
                _, sizes = format_sizes(sizes, factor=denominator)
                # And plot them
                sub_ax.plot(tmp_list, sizes, label=dir_name)
                plotted += 1
            format_dates(sub_ax)
            sub_ax.set_title(f'Top {plotted} directories with the highest mean size')
            sub_ax.set_xlabel("Date")
            sub_ax.set_ylabel(f"Size in {denominator}")
            sub_ax.legend()

        def format_dates(target_ax) -> None:
            # Convert displayed timestamps to human-readable dates
            target_ax.get_xaxis().set_major_formatter(
                FuncFormatter(lambda tm, p: strftime(date_format, gmtime(tm)))
            )

        def format_sizes(sizes_list: List[int], factor: Union[int, str] = 'auto') -> Tuple[str, List[int]]:
            """
            Format the sizes in `sizes_list` using `factor` if specified,
            otherwise guess it.
            :param sizes_list: The list of sizes to format.
            :param factor: Factor used to divide the size,
                           by default in bytes, to a more readable range.
                           Can be an integer, i.e. 1 for KB, 2 for MB, 3 for GB...
                           A string, i.e.g 'KB', 'MB', 'GB'...
                           'auto' for automatic casting
            """
            size_range_map = ['B', 'KB', 'MB', 'GB', 'TB']
            if factor == 'auto':
                max_size = max(sizes_list)
                for i in range(len(size_range_map)):
                    if max_size / (1024 ** i) < 1024:
                        factor = i
                        break
                else:
                    # If we reach the end of the for loop,
                    # we use the highest factor we can.
                    factor = len(size_range_map) -1
            elif isinstance(factor, str):
                try:
                    factor = size_range_map.index(factor)
                except ValueError:
                    raise ValueError(
                        f'Invalid factor: got {factor!r}, '
                        f'expected any of {size_range_map}'
                    )
            else:
                raise ValueError(
                    f"Invalid factor: got {factor!r}, "
                    f"expected 'auto' or integer"
                )

            # Here, factor is necessarily an integer,
            # though it might still be out of range
            try:
                denominator = size_range_map[factor]
            except IndexError:
                raise ValueError(
                    f'Invalid factor: should be an integer in range '
                    f'(0, {len(size_range_map)})'
                )

            # `factor` and `denominator` are valid

            formatted_sizes = [
                round(size / (1024 ** factor), 3)
                for size in sizes_list
            ]

            return denominator, formatted_sizes

        # Construct the timestamp list.
        # It is ordered from the least recent (first)
        # to the most recent (last).
        timestamp_list = [
            self.rr[i][0]
            for i in range(len(self.rr))
            if self.rr[i] != self.default_value
        ]

        all_dirs: AllType = {}
        for i in range(len(self.rr)):
            instance: InstanceType = self.rr[i]

            if instance == self.default_value:
                continue

            # Iterate over the directories census
            for dir_path, dir_size in instance[1]:

                dir_name = dir_path.name

                # Append the size to the right dictionary value.
                try:
                    all_dirs[dir_name].append(dir_size)
                except KeyError:
                    # If a KeyError is raised,
                    # meaning the directory could not be found
                    # in the dictionary, we add it with its first value.
                    all_dirs.update({dir_name: [dir_size]})

        fig, ax = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

        top_mean_plot(timestamp_list, all_dirs, ax[0])
        widest_range_plot(timestamp_list, all_dirs, ax[1])

        print('Showing dashboard')
        plt.show()


###############
# ARGS PARSER #
###############

parser = argparse.ArgumentParser(
    "Python3 utility used to keep track of the disk usage "
    "of a directory per subdirectory over time."
)

parser.add_argument("-d", "--directory",
                    help="Directory to scan recursively. "
                         "Must be an absolute path.",
                    type=str, nargs=1)
parser.add_argument("-f", "--file",
                    help="The path of the file in which "
                         "we will store the results.",
                    type=str, nargs=1)
parser.add_argument("-o", "--occurrence",
                    help="Delay in seconds to apply between each parsing. "
                         "Default is 24 hours.",
                    type=int, nargs=1)
parser.add_argument("-i", "--instances",
                    help="How many instances we want reported at most. "
                         "Default is 30.",
                    type=int, nargs=1)
parser.add_argument("-r", "--run",
                    help="Optional. Run for n times. "
                         "Specify 0 to run indefinitely.",
                    type=int, nargs=1)
parser.add_argument("--dashboard",
                    help="Display a dashboard after running. "
                         "Default is False, specify for True.",
                    action="store_true")


args = parser.parse_args()

if args.directory:
    root_directory = Path(args.directory[0]).resolve()
else:
    root_directory = Path(os.getcwd()).resolve()  # Current directory

if args.file:
    output_file = Path(args.file[0]).resolve()
else:
    output_file = Path('./du.db').resolve()  # In the current directory

if args.occurrence:
    delay_between_two = args.occurrence[0]
else:
    delay_between_two = 60 * 60 * 24

if args.instances:
    instances = args.instances[0]
else:
    instances = 30

if args.run:
    n = args.run[0]
else:
    n = None

if args.dashboard:
    dashboard = True
else:
    dashboard = False


if __name__ == "__main__":
    print(f'Launched on {datetime.now()}')
    du = DirectoryUsage(root=root_directory,
                        trace=instances,
                        delay=delay_between_two,
                        file_location=output_file)

    if isinstance(n, int):
        if n == 0:
            du.run_forever()
        else:
            du.run_for(n)

    print(f'Ended on {datetime.now()}')

    if dashboard:
        du.dashboard()
