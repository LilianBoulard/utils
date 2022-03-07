"""
Script used to convert a directory usage rrdb with string paths (type str)
to a path object from pathlib (pathlib.Path).
"""


from pathlib import Path
import round_robin as rr
from typing import Tuple, List

fl = Path('./old_db.rrdb').resolve()
new_fl = Path('./new_db.rrdb').resolve()

rrdb = rr.RoundRobin.read_from_disk(fl)
new_rrdb = rr.RoundRobin(file_location=new_fl, length=30, default_value=[])

InstanceType = Tuple[int, List[Tuple[Path, int]]]

new_instances = []
for i in range(len(rrdb)):
    it = rrdb[i]

    if not it:
        continue

    tmp, instance = it
    instance = [(Path(p), int(i)) for p, i in instance]
    new_instances.append((tmp, instance))

for instance in new_instances:
    new_rrdb.append(instance)

new_rrdb.write_to_disk()
