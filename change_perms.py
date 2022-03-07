"""
Change file and dir permissions recursively.
"""

from pathlib import Path


def change_perm(directory: Path) -> None:
    for item in directory.iterdir():
        if item.is_dir():
            change_perm(item)
            item.chmod(dir_perms)
        elif item.is_file():
            item.chmod(file_perms)


if __name__ == "__main__":
    root = Path.cwd()
    dir_perms = 0o755
    file_perms = 0o640
    change_perm(root)
