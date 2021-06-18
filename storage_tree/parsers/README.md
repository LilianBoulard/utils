# Parsers

We will find in this directory parsers, which are used to convert the output of a script 
(for instance, ``files_to_dataframe``, which outputs a `pandas.DataFrame` stored in `parquet`)
to a tree structure.

After parsing this content, it will be processed by a view, for visualization of the data.  
See ``storage_tree/views/README.md`` for views' documentation.


## Implementing a new parser

To implement a new parser, follow this process:

First, create a new Python file with the name of your parser.  
The name should be lowercase, and contain no special character (spaces forbidden).
It should be kept simple and to-the-point.

For instance, if you're creating a parser for `files_to_dataframe`, you could name it `ftd.py`:

    touch ftd.py

Next, write a new class `Parser` (it **must** have this name),
which will inherit `BaseParser`, from `base`.

```python
from .base import BaseParser

class Parser(BaseParser):
    pass
```

Next up, there are two mandatory methods to implement:

- ``_read_file``
- ``_get_content``

They are extensively documented in the source code ``storage_tree/parsers/base.py``.

```python
import pandas as pd
from typing import Dict
from .base import BaseParser


class Parser(BaseParser):
    
    ReadFileStructure = pd.DataFrame
    
    def _read_file(self) -> ReadFileStructure:
        """
        Reads the input file, stored in `self.file`,
        and returns a data structure that will be used in `_get_content()`.
        """
        pass

    def _get_content(self) -> Dict[str, int]:
        """
        Processes `raw_content`, and returns a list of tuples,
        which themselves contain (1) the absolute file path,
        and (2) the size of this file in bytes.
        """
        pass
```

From there, we just have to write the actual processing

```python
import pandas as pd

from typing import Dict
from pathlib import Path

from .base import BaseParser


class Parser(BaseParser):

    ReadFileStructure = pd.DataFrame

    PATHS_COLUMN = 'path'
    SIZES_COLUMN = 'size'

    def _read_file(self) -> ReadFileStructure:
        return pd.read_parquet(self.file, engine='fastparquet')

    def _get_content(self) -> Dict[Path, int]:

        def to_path(path: str) -> Path:
            return Path(path)

        return dict(
            zip(
                self.raw_content[self.PATHS_COLUMN].apply(to_path).to_list(),
                self.raw_content[self.SIZES_COLUMN].to_list()
            )
        )
```
