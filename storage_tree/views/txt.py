from .base import BaseView


class View(BaseView):

    @staticmethod
    def std_repr(obj):
        # Compute indentation
        indent = obj.level * "  "
        # Create string:
        # We add the indentation, then the directory's name,
        # then a slash, to indicate it is a directory.
        r = f"{indent}{obj.name}/\n"
        # For each children the directory has,
        for child in obj.children:
            # We'll just append the repr of each child.
            # As we'll see in the next method, 
            # it takes care of properly displaying itself.
            r += repr(child)
        # Return the full string
        return r

    @staticmethod
    def stf_repr(obj):
        # Compute indentation
        indent = obj.level * "  "
        # Same as above, except this time not slash,
        # but the size of the object 
        # (in bytes, see code of `storage_tree.StorageTreeFile`).
        r = f"{indent}{obj.name} - {obj.size}\n"
        # Return the string
        return r

    @staticmethod
    def st_repr(obj):
        # Just return the repr of the root, 
        # which is the root StorageTreeDirectory.
        return repr(obj.root)
