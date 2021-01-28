# -*- coding: utf-8 -*-

import storage_tree


class View:

    @staticmethod
    def std_repr(obj):
        indent = obj.level * "  "
        r = f"{indent}{obj.name}/\n"
        for child in obj.children:
            r += child.__repr__()
        return r

    @staticmethod
    def stf_repr(obj):
        indent = obj.level * "  "
        r = f"{indent}{obj.name} - {obj.size}\n"
        return r

    @staticmethod
    def st_repr(obj):
        return obj.root.__repr__()


if __name__ == "__main__":
    storage_tree = storage_tree.StorageTree(storage_tree.pydu_result_file, view=View)
    print(storage_tree)
