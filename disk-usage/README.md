# Disk-usage

This system is divided in two parts:
1. the utility script ``disk_usage.py``, which is in charge of scanning a directory (and its subdirectories) to get the ``n`` heaviest files.
2. a tree data structure of the ``disk_usage``'s output, which can be used to visualize the data.

## Usage

### Disk usage

To get more information on how to use the disk usage script, launch 

    python disk_usage.py -h

When launching a scan, it is advised to pipe the output (which by default is sent to ``stdout``) to a file, 
so that you can use the storage tree script later on.

On linux:

    python disk_usage -n 50 > ~/disk_usage_output.txt

### Storage tree

*Files mentioned below are located in the directory ``storage_tree``*

#### Data structure

A tree data structure can be constructed from the output of the ``disk_usage.py`` script.

The base file is ``storage_tree/storage_tree.py``.
\
You won't be launching it directly: instead, we'll use ``views``.

#### Custom views

Once the tree is constructed, we can use a custom view to create a visualization of the data: 
TXT, HTML, CSV, XML, and so on ; you decide !

A few examples are available under the format ``X_view.py``.
\
Further documentation is available in the source code.

#### Usage:

As we did with ``disk_usage``, we will pipe the output to a file.

    python HTML_colored_view.py -s ~/disk_usage_output.txt > ~/disk_usage_output.html
