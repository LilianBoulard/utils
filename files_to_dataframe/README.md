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

## Usage

All the files can be used with the same format:  
Launch

    python3 <script>.py -h

To get the available parameters and their description.

## Files

1. ``files_to_dataframe.py`` parses the directory and constructs the DataFrame, storing it locally afterwards.  
   *Note on naming conventions: The dataframe is stored as `<formatted_path>_persistent.df`*
2. ``post_processing.py`` extracts interesting features from the DataFrame, and adds them as new columns.

One more column is created upon running ``post_processing.py``:
- ``extension`` - the extension of the file.

### Optional

- ``by_extension.py`` contains utilities to manipulate the files' information based on their extension.
- ``describe_dataframe.py`` can be used to describe a DataFrame and gain some insights on its content.
