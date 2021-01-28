#!/usr/bin/env python
# coding: utf-8

import os
import sys
import logging
import platform
import argparse

from functools import wraps
from datetime import datetime
from typing import List, Tuple
from time import time, gmtime, strftime


def time_it(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        timer_start = time()
        returned = func(*args, *kwargs)
        timer_stop = time()
        time_it_took = timer_stop - timer_start
        st = (f"The function {func.__name__!r} took {time_it_took:.2f} seconds"
              f" ({strftime('%H:%M:%S', gmtime(time_it_took))}).")
        logging.info(st)
        return returned

    return wrapper


class DiskUsage:

    # All the values below are case-sensitive.
    # Only use "/" as the separator, regardless of your OS.

    # Files with these extensions should not be scanned. Do not include the leading dot.
    # e.g. ["iso", "mp4"]
    excluded_ext: List[str] = []
    # Specific file names that should not be included. Include the extension.
    # e.g. ["file.txt", "log.log"]
    excluded_files_names: List[str] = []
    # Files that should not be scanned. Absolute paths only.
    # e.g. ["/this/file.txt", "that/specific/log.log"]
    excluded_files: List[str] = []
    # Names of directories that should not be scanned.
    # Do not include the first or last separator.
    # e.g. ["Dropbox", ".cache"]
    excluded_directories_names: List[str] = []
    # Directories that should not be scanned. Absolute paths only.
    # Do not include the last separator.
    # e.g. ["/proc", "/home/user/.cache"]
    excluded_directories: List[str] = []

    def __init__(self, max_results: int, threshold: int = 0):
        """
        :param int max_results: How many files we want to return at most.
        :param int threshold: A value in bytes. We will not include files with a smaller size.
        """
        self.src = None
        self.max_results: int = max_results
        self.threshold: int = threshold
        self.lightest_file_size: int = self.threshold
        self._du: List[Tuple[str, int]] = []

    @time_it
    def scan(self, src: str) -> None:
        """
        :param str src: The source directory path. Must be absolute.
        """
        if not os.path.isabs(src):
            raise ValueError("The source path must be absolute.")
        self.src: str = src
        self._dir_scan(self.src)

    def return_results(self, human_readable: bool) -> List[Tuple[str, int]] or List[Tuple[str, str]]:
        """
        :param bool human_readable: Whether to convert the sizes in human-readable format.
        :return list: The disk usage result.
        """
        if human_readable:
            units = ["B", "KB", "MB", "GB", "TB"]
            hr_du: List[Tuple[str, str]] = []
            for result in self._du:
                file_size, size = result  # Unpack the tuple
                unit_index = 0
                while size >= 1024:
                    size /= 1024
                    unit_index += 1
                b = units[unit_index]  # Could raise an IndexError if the file is above or equal to 1024TB.
                size = f"{int(size)}{b}"
                hr_du.append((file_size, size))
            return hr_du
        else:
            return self._du

    def _insert_sorted(self, value: Tuple[str, int]) -> None:
        """
        Inserts a new value in a sorted list.
        Instead of calling the builtin function ``sort()`` which is very slow,
        we iterate the ``du`` list and we add the tuple at the right place.
        The first item of the list is the heaviest file.

        :param Tuple[str, int] value: A tuple containing the name of the file, and its size in bytes.
        """
        du_length = len(self._du)
        if du_length == 0:
            self._du.append(value)
        else:
            new_file_name, new_size = value
            for index, file_info in enumerate(self._du):
                size = file_info[1]
                if new_size > size:
                    self._du.insert(index, value)
                    break
        if du_length == self.max_results:
            self._du.pop(-1)  # Remove last item

        self.lightest_file_size = self._du[-1][1]

    def _file_scan(self, src: str) -> None:
        """
        :param str src: Absolute path of the file to process.
        """
        logging.debug(f"Processing file {src!r}")

        try:
            file_size = os.path.getsize(src)
        except UnicodeEncodeError:
            logging.warning(f"UnicodeEncodeError: Could not scan file {src!r}")
        except PermissionError:
            logging.warning(f"PermissionsError: Could not scan file {src!r}")
        except OSError:
            logging.warning(f"OSError: Could not scan file {src!r}")
        else:
            if file_size > self.lightest_file_size:
                self._insert_sorted((src, file_size))

    def _dir_scan(self, src: str) -> None:
        """
        Scans a directory.
        Used recursively.

        :param str src: Absolute path to the directory to scan.
        """
        logging.debug(f"Processing directory {src!r}")

        try:
            for p in os.listdir(src):
                p_path = os.path.join(src, p)
                if not os.path.islink(p_path):

                    if os.path.isdir(p_path):
                        if p_path in self.excluded_directories:
                            continue
                        if p in self.excluded_directories_names:
                            continue
                        self._dir_scan(p_path)

                    elif os.path.isfile(p_path):
                        if p_path in self.excluded_files:
                            continue
                        if p in self.excluded_files_names:
                            continue
                        if len(self.excluded_ext) > 0:
                            # We first check if the list is empty, to avoid splitting the file name for nothing.
                            ext = p.split(".")[-1]
                            if ext in self.excluded_ext:
                                continue
                        self._file_scan(p_path)

        except PermissionError:
            logging.warning(f"[PermissionsError] Could not process directory {src!r}")


###############
# ARGS PARSER #
###############

parser = argparse.ArgumentParser("A disk usage utility in Python3.")

parser.add_argument("-r", "--root",
                    help="Directory to scan recursively. Must be an absolute path.",
                    type=str, nargs=1)
parser.add_argument("-l", "--logs",
                    help="Absolute path to the directory where log files will be stored.",
                    type=str, nargs=1)
parser.add_argument("-n",
                    help="How many files do we want reported at most. Default is 50.",
                    type=int, nargs=1)
parser.add_argument("-t", "--threshold",
                    help="A size in bytes. Files under this threshold will not be reported. Default is 0.",
                    type=int, nargs=1)
parser.add_argument("-hr", "--human-readable",
                    help="Converts the files sizes to human-readable format. False by default, specify for True.",
                    action="store_true")

cl_args = parser.parse_args()

if cl_args.root:
    root = cl_args.root[0]
else:
    root = "/"

if cl_args.logs:
    log_dst = cl_args.logs[0]
else:
    log_dst = "/tmp/pydu_log/"

if cl_args.human_readable:
    human_readable = True
else:
    human_readable = False

if cl_args.n:
    n = cl_args.n[0]
else:
    n = 50

if cl_args.threshold:
    threshold = cl_args.threshold[0]
else:
    threshold = 0


########
# LOGS #
########

logging_level = logging.INFO


def create_log_file(log_dir: str, log_path: str) -> None:
    if not os.path.isabs(log_dir) or not os.path.isabs(log_path):
        raise ValueError("The log path must be absolute.")
    try:
        os.makedirs(log_dir)
    except FileExistsError:
        pass
    open(log_path, "w").close()


logfile = os.path.join(log_dst,
                       f"pyDiskUsageReport-{datetime.now().year}-{datetime.now().month}-{datetime.now().day}-"
                       f"-{datetime.now().hour}-{datetime.now().minute}.txt")

create_log_file(log_dst, logfile)

logger = logging.getLogger()
logger.setLevel(logging_level)

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
formatter.datefmt = '%m/%d/%Y %H:%M:%S'

# Output to file
fh = logging.FileHandler(filename=logfile, mode='w')
fh.setLevel(logging_level)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Output to stdout
# Uncomment for debugging purposes ; using it will break the processing done by storage tree (if used).
# sh = logging.StreamHandler(sys.stdout)
# sh.setLevel(logging_level)
# sh.setFormatter(formatter)
# logger.addHandler(sh)


########
# MAIN #
########

if __name__ == "__main__":
    if platform.system() != "Linux":
        input("WARNING: This script has been designed for Linux. Press enter to proceed anyway...")

    du = DiskUsage(n, threshold)
    logging.info(f"Launching Disk Usage scan on {root!r}")
    du.scan(root)

    results = du.return_results(human_readable=human_readable)

    for r in results:
        print(r)
    print(len(results))
