"""
Provides tools to analyze the files based on their extension.
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


extension_column_name = 'extension'


def get_file_count_by_extension(dataframe):
    """
    Returns a dictionary mapping containing as key the extension,
    and as value the total number of files of this type.
    """
    count = {}
    for ext in dataframe[extension_column_name].unique():
        count[ext] = dataframe[dataframe[extension_column_name] == ext].shape[0]
    return count


def get_total_size_by_extension(dataframe):
    """
    Returns a dictionary mapping containing as key the extension,
    and as value the total size this type of file occupies in bytes.
    """
    total_size = {}
    for ext in dataframe[extension_column_name].unique():
        all_files_by_ext = dataframe[dataframe[extension_column_name] == ext]
        total_size[ext] = all_files_by_ext['size'].sum()
    return total_size


def sort_dict(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda pair: pair[1]))


def pie_chart(dictionary: dict, threshold: float) -> None:
    """
    Displays a pie chart of the data passed.

    :param dict dictionary: Dictionary to analyze.
    :param int threshold: Ranges from 0.0 to 100.0.
                          Values representing less than this percentage
                          will be aggregated in a single dummy value.
    """

    def func(percentage, all_values):
        """
        Used to convert sizes to readable values.
        """
        absolute = int(percentage / 100. * np.sum(all_values))
        return "{:.1f}%\n{:.1f}GB".format(percentage, absolute / (1024 ** 3))

    # Calculate threshold value
    total = sum(dictionary.values())
    threshold_value = int(total * (threshold / 100))
    # Apply threshold ; sizes under the threshold value are aggregated.
    dictionary = {k: v for k, v in dictionary.items() if v > threshold_value}
    # Add the "Others" value
    diff = total - sum(dictionary.values())
    dictionary.update({'Others': diff})
    # Sort the dictionary again, to place "Others" correctly.
    dictionary = sort_dict(dictionary)

    # Extracts sets
    labels = list(dictionary.keys())
    uses = list(dictionary.values())
    # Display pie
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.pie(uses, labels=labels, startangle=140, autopct=lambda pct: func(pct, uses))
    ax.set_title(f'Disk usage of {file!r} by extension')
    plt.show()


###############
# ARGS PARSER #
###############

parser = argparse.ArgumentParser(
    'Utility used to read a serialized DataFrame generated by "files_to_dataframe.py", '
    'and show the usage of the root directory by extension type.'
)

parser.add_argument("-f", "--file",
                    help="Path to the file that contains "
                         "the serialized DataFrame.",
                    type=str, nargs=1, required=True)
parser.add_argument("--pie",
                    help="Displays a pie chart at the end of the execution. "
                         "False by default, specify for True",
                    action="store_true")
parser.add_argument("--pie-threshold",
                    help="Threshold used to simplify the pie chart. "
                         "It is a percentage expressed between 0.0 and 100.0. "
                         "All values representing less than this "
                         "percentage of the total will be aggregated together. "
                         "Default is 1.0, which is 1 percent.",
                    type=float, nargs=1)

args = parser.parse_args()

file = args.file[0]

if args.pie:
    pie = True
else:
    pie = False

if args.pie_threshold:
    pie_threshold = args.pie_threshold[0]
else:
    pie_threshold = 1.0  # 1%


if __name__ == '__main__':
    # Import df
    df = pd.read_parquet(file)

    # The DataFrame has two columns:
    # 1. path
    #   - The full path of the file
    # 2. size
    #   - The file's size, in bytes
    # 3. extension
    #   - The file's extension, empty if it does not have one

    sizes = sort_dict(get_total_size_by_extension(df))
    if pie:
        pie_chart(sizes, pie_threshold)
