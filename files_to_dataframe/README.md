# Files-to-DataFrame

These scripts are designed to store files' information in a pandas DataFrame for further processing.  
Currently, two columns are created:
- ``path`` - the absolute path of the file
- ``size`` - the size of this file in bytes

One more is created after running ``post-processing.py``:
- ``extension`` - the extension of the file

## Usage

1. ``files_to_dataframe.py`` parses the directory and constructs the DataFrame, 
  storing it locally afterwards.
2. ``post_processing.py`` extracts interesting features from the DataFrame.

## Other files

- ``by_extension.py`` contains utilities to manipulate the files' information based on their extension.
- ``describe_dataframe.py`` can be used to describe a DataFrame and gain some insights on its content.
