from pathlib import Path
from typing import Dict, List

import pandas as pd

from ._utils import log_duration


class Dashboard:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @log_duration('Generating dashboard')
    def generate(self, output_file: Path, data: Dict[str, List[int]]) -> None:
        """
        Takes a dictionary `data` containing as key
        a hash, and as value a list of integers,
        which are the indices of the files with this hash,
        and creates a HTML dashboard, which is sent to `output_file`.
        """
        html = "<html>"
        # Add some css in the head.
        html += "<head>"
        html += "<style>"
        html += "table, th, td { border: 1px solid black; border-collapse: collapse }"
        html += "th, td { padding: 5px; text-align: left; }"
        html += "</style>"
        html += "</head>"
        # Create the body
        html += "<body>"
        for h_str, indices in data.items():
            # We create a new table for each hash
            html += '<table style="width:100%">'
            for i, index in enumerate(indices):
                html += "<tr>"
                if i == 0:
                    # If we're at the first line, add the hash
                    html += f'<th rowspan="{len(indices)}">{h_str}</th>'
                html += f"<td>{self.df.loc[index]['path']}</td>"
                html += "</tr>"
            html += "</table>"
        html += "</body>"
        html += "</html>"

        output_file.write_text(data=html)
