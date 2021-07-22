import pandas as pd

from pathlib import Path
from hashlib import sha256
from typing import Dict, Any

from ._parser import Parser
from ._utils import read_dataframe


class DuplicateParser:

    # When hashing a file, how much data we want to read at once.
    buffer = 1024 ** 3

    def __init__(self, directory: Path, mem_limit: int = 2147483648):
        self.parser = Parser(directory, mem_limit)
        self.parser.run(
            structure=[
                'path',
                'hash',
            ],
            file_callback=self.extract_from_file,
            directory_callback=None,
            optimization_callback=None,
        )

    def hash_file(self, file_path):
        """This function returns the SHA-1 hash
        of the file passed into it"""
        h = sha256()
        with open(file_path, 'rb') as file:
            chunk = 0
            while chunk != b'':
                chunk = file.read(self.buffer)
                h.update(chunk)
        return h.hexdigest()

    def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        h = self.hash_file(file_path)
        return {
            'path': file_path,
            'hash': h,
        }

    def get_final_df_path(self):
        return self.parser.get_final_df_path()

    def get_final_df(self) -> pd.DataFrame:
        return read_dataframe(self.get_final_df_path())
