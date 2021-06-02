# Round-Robin database

This module implements a simple Round-Robin database.

It can be used to store a fixed, rotating set of information.

For instance, to keep track of the temperature of a room on an hourly basis over the last month
(24 hours * 30 days = 720 database instances).

## Directory usage over time

The script ``rrdb_directory_usage.py`` can be used to keep track 
of the disk usage of a directory per sub-directory over time.

### Usage

To print the script's documentation, use 

    python rrdb_directory_usage.py -h
