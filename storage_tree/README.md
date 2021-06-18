# Storage tree

Storage tree is a visualization script.  
It takes files information input of any format, 
constructs a [tree](https://en.wikipedia.org/wiki/Tree_(data_structure)) 
and returns a visualization.

## Usage

For more information on how to use the script, launch

    python3 storage_tree.py -h

It will output the list of parameters available, and how to use them.


## Input

The input contains information about files, 
namely their path and size.  
It can come from any script and have any structure.  
We will use a parser to convert its content to a tree.  

If one already exists for the script you're using, then great !

Otherwise, refer to the next section to know how to create a new one.

### New input - Create a parser

If a parser doesn't exist already for your data, 
you can create a new one by following the process described extensively in 
``storage_tree/parsers/README.md`` and ``storage_tree/parsers/base.py``.


## Views

To output the tree in a readable format, we use a view.  

Common ones are already implemented, and can be found in ``storage_tree/views/``.

### Create a new view

The process of creating a new view is extensively described in 
``storage_tree/views/README.md`` and ``storage_tree/views/base.py``.
