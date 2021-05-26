# n_most

*Formerly disk-usage*

Utility script in charge of scanning a directory 
(and its subdirectories ; recursively) to get the ``n`` heaviest files.

## Usage

To get more information on how to use the disk usage script, launch 

    python3 disk_usage.py -h

When launching a scan, it is advised to pipe the output (which by default is sent to ``stdout``) to a file, 
so that you can use a visualization tool later on (for instance `storage_tree`).

On linux:

    python3 disk_usage.py -n 50 > ~/disk_usage_output.txt
