import os

import pandas as pd

from pathlib import Path
from typing import Dict, Union

from ._parser import Parser


class FTDParser:

    def __init__(self, directory: Path, mem_limit: int = 2147483648, file_size_threshold: int = 1024):
        # Files under this size (in bytes) will not be registered.
        self.file_size_threshold = file_size_threshold
        self.parser = Parser(directory, mem_limit)
        self.parser.run(
            structure=['path', 'size', 'uid', 'atime', 'mtime'],
            file_callback=self.extract_from_file,
            optimization_callback=self.optimize,
        )

    def extract_from_file(self, file_path: str) -> Dict[str, Union[str, int]]:
        try:
            file_stat = os.stat(file_path)
        except (PermissionError, FileNotFoundError, OSError):
            return {}

        file_size = file_stat.st_size

        if file_size > self.file_size_threshold:
            return {
                'path': file_path,
                'size': file_size,
                'uid': file_stat.st_uid,
                'atime': file_stat.st_atime,
                'mtime': file_stat.st_mtime,
            }
        else:
            return {}

    @staticmethod
    def optimize(df: pd.DataFrame) -> pd.DataFrame:
        # Cast to more efficient types
        if df['uid'].max() > 65535:
            uid_type = 'uint32'
        else:
            uid_type = 'uint16'
        df = df.astype({
            'path': 'string',
            'size': 'uint64',
            'uid': uid_type,
            'atime': 'uint32',  # Will work until February 2106
            'mtime': 'uint32',  # Will work until February 2106
        })

        return df
