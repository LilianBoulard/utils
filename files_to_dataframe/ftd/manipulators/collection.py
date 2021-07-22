from .base import BaseManipulator
from . import ByUserManipulator, ByDateManipulator, ByExtensionManipulator, ByDirectoryManipulator, BySizeManipulator


class ManipulatorCollection:

    """
    This class is used to instantiate all the manipulators
    """

    def __init__(self, **kwargs):

        # Forbid passing "parent"
        if 'parent' in kwargs.keys():
            raise RuntimeError('Got unexpected argument "parent" in keyword arguments')

        self.user_manipulator = ByUserManipulator(parent=self, **kwargs)
        self.date_manipulator = ByDateManipulator(parent=self, **kwargs)
        self.ext_manipulator = ByExtensionManipulator(parent=self, **kwargs)
        self.dir_manipulator = ByDirectoryManipulator(parent=self, **kwargs)
        self.size_manipulator = BySizeManipulator(parent=self, **kwargs)

        self.all_manipulators = [
            self.user_manipulator,
            self.date_manipulator,
            self.ext_manipulator,
            self.dir_manipulator,
            self.size_manipulator
        ]

    def call_method(self, method_name: str, **kwargs):
        if hasattr(BaseManipulator, method_name):
            for man in self.all_manipulators:
                getattr(man, method_name)(**kwargs)
        else:
            raise RuntimeError(f'No such function of manipulator: {method_name}')
