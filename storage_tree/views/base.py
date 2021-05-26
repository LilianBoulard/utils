def human_readable_bytes(size: int) -> str:
    """
    Takes a size in bytes and returns it human-readable.

    :param int size: A size, in bytes.
    :return str: A readable size. e.g. 5 GB, 14 MB, 1 TB...
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size >= 1024:
        size /= 1024
        unit_index += 1
    b = units[unit_index]  # Could raise an IndexError if the file size is above or equal to 1024TB.
    size = f"{int(size)} {b}"
    return size


class BaseView:

    """
    To create a new view (a new way of visualizing the tree),
    inherit this class and override the three following functions.
    Refer to `README.md` for more information.
    """

    @staticmethod
    def std_repr(obj) -> str:
        """
        Mocks `StorageTreeDirectory.__repr__()`.

        Represents a node (directory).
        As it is a tree (and therefore is recursive),
        this method should call the object's child `__repr__` magic method:
        ``obj.child.__repr__()``
        Note: child can either be another `StorageTreeDirectory`,
        or a `StorageTreeFile`.

        :param StorageTreeDirectory obj:
        :return str:
        """
        raise NotImplemented

    @staticmethod
    def stf_repr(obj) -> str:
        """
        Mocks `StorageTreeFile.__repr__()`.

        Represents a leaf (file).

        :param StorageTreeFile obj:
        :return str:
        """
        raise NotImplemented

    @staticmethod
    def st_repr(obj) -> str:
        """
        Mocks `StorageTree.__repr__()`.

        Represents the root (storage tree).
        As it is a tree (and therefore is recursive),
        this method should call the object's root `__repr__` magic method:
        ``obj.root.__repr__()``
        Note: root is a `StorageTreeDirectory`.
        This method is only called once, which allows you to wrap the output.

        :param StorageTree obj:
        :return str:
        """
        raise NotImplemented
