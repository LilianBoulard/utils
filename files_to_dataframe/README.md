*Original sources at https://github.com/LilianBoulard/utils/tree/main/files_to_dataframe*

# Files-to-DataFrame (FTD)

A set of scripts designed to store files' information in a pandas DataFrame and post-process that output.  
It parses recursively a directory specified, 
and outputs the useful information to a DataFrame stored in Apache Parquet.

Upon running, five columns are created:
- ``path`` - the absolute path of the file
- ``size`` - the size of this file in bytes
- ``uid`` - the system ID of the owner of the file
- ``atime`` - UNIX timestamp of the last access to the content
- ``mtime`` - UNIX timestamp of the last modification of the content

and two more are added during post-processing:
- ``extension`` - the extension of the file
- ``username`` - the readable username correlated to the `uid`

## Usage

There are two main scripts:
- ``parse_and_post_process.py`` which parses a directory, and post-processes the output.
- ``stats.py`` which is used for later analytics

To get the available parameters and their documentation, launch

    python3 <script>.py -h


Two more columns are created upon running ``post_processing.py``:


### Optional

- ``ftd/describe_dataframe.py`` can be used to describe a DataFrame and gain some insights on its content.
