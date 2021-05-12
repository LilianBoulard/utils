# Files-to-DataFrame

These scripts are designed to store files' information in a pandas DataFrame for further processing.  
Currently, two columns are created:
1. ``path`` - the absolute path of the file
2. ``size`` - the size of this file in bytes

## Files

- ``files_to_dataframe.py`` parses the directory and constructs the DataFrame, 
  storing it locally afterwards.
- ``by_extension.py`` contains utilities to manipulate the files' information based on their extension.
