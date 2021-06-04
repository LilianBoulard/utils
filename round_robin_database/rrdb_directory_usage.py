"""
Round-Robin database used to monitor the usage
of a directory per subdirectories over time.
"""

import os
import argparse

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from math import floor
from datetime import datetime
from typing import List, Tuple, Dict
from time import sleep, time, strftime, gmtime

import round_robin as rr


# Type hint of the structure to store.
# An instance contains a tuple with
# (1) the timestamp of the transaction (UNIX seconds)
# (2) a list of tuples, each containing
# (1) the path (absolute or relative) to the directory
# (2) the size, in bytes, of this directory.
InstanceType = Tuple[int, List[Tuple[str, int]]]


class DirectoryUsage:

    """
    A Round-Robin database storing the usage of subdirectories of a root dir.
    Useful for visualization of the usage over time.
    """

    default_value = []

    def __init__(self, root: str, trace: int, delay: int, file_location: str):
        self.root = root
        self.delay = delay
        self.file_location = file_location

        # Read the database from file if found, otherwise init.
        if os.path.exists(file_location):
            print(f'Reading database {file_location!r}')
            self.rr = rr.RoundRobin.read_from_disk(file_location)

        if not os.path.exists(file_location) or len(self.rr) != trace:
            print(f'No database found on disk, '
                  f'creating a new one: {file_location!r}')
            self.rr = rr.RoundRobin(length=trace,
                                    default_value=self.default_value,
                                    file_location=file_location)

        # Dashboard values
        self.fig = None

        self._running: bool = True

    def wait(self) -> None:
        sleep(self.delay)

    def is_running(self) -> bool:
        return self._running

    def get_directory_size(self, directory: str) -> int:
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

    def list_directories(self) -> List[str]:
        """
        Parses the root and returns the list of directories it contains.
        """
        dirs = []
        for p in os.listdir(self.root):
            path = os.path.join(self.root, p)
            if os.path.isdir(path):
                dirs.append(path)
        return dirs

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

    def dashboard(self, date_format: str = '%c') -> None:
        """
        Creates a dashboard.

        :param str date_format: Date format to use on the plot.
        See https://docs.python.org/3/library/time.html#time.strftime

        TODO: Cleanup and better handle missing values
        """

        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot()
        ax.set_title(f'Disk usage of {self.root!r} by directory')
        ax.set_xlabel("Date")
        ax.set_ylabel("Size in MB")

        # Construct the timestamp list.
        # It is ordered from the least recent (first)
        # to the most recent (last).
        timestamp_list = [
            self.rr[i][0]
            for i in range(len(self.rr))
            if self.rr[i] != self.default_value
        ]

        all_dirs: Dict[str, List[int, ...]] = {}
        for i in range(len(self.rr)):
            instance: InstanceType = self.rr[i]

            if instance == self.default_value:
                continue

            # Iterate over the directories census
            for dir_path, dir_size in instance[1]:

                # Get only the tail of the directory path.
                dir_name = os.path.split(dir_path)[1]

                # Append the size to the right dictionary value.
                try:
                    all_dirs[dir_name].append(dir_size)
                except KeyError:
                    # If a KeyError is raised,
                    # meaning the directory could not be found
                    # in the dictionary, we add it with its first value.
                    all_dirs.update({dir_name: [dir_size]})

        for dir_name, sizes in all_dirs.items():

            # Convert sizes to megabytes
            formatted_sizes = [
                round(size / (1024 ** 2), 3)
                for size in sizes
            ]

            ax.plot(timestamp_list, formatted_sizes, label=dir_name)

        # Convert displayed timestamps to human-readable dates
        ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda tm, p: strftime(date_format, gmtime(tm)))
        )

        plt.legend()
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
    root_directory = args.directory[0]
else:
    root_directory = os.getcwd()  # Current directory

if args.file:
    output_file = args.file[0]
else:
    output_file = 'du.db'  # In the current directory

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
