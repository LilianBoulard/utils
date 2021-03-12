# -*- coding: utf-8 -*-

import storage_tree


list_styles = ['disc', 'circle', 'square']


class View:

    @staticmethod
    def std_repr(obj: storage_tree.StorageTreeDirectory) -> str:
        """
        :param storage_tree.StorageTreeDirectory obj:
        :return str:
        """
        parent = obj.parent
        children = obj.children

        is_parent_st = isinstance(parent, storage_tree.StorageTree)

        if is_parent_st:
            siblings = 0
        else:
            siblings = len(parent.children) - 1

        r = ""

        if is_parent_st:
            r += "<li>"

        if siblings == 0:
            r += f"{obj.name}/"
        elif siblings > 0:
            r += f"<li>{obj.name}/"

        # Additional value that can be added at the end of every directory line.
        eol = f" ({storage_tree.human_readable_bytes(obj.size)})"

        if len(children) == 1:
            # If we have only one child.
            child = children[0]
            is_child_std = isinstance(child, storage_tree.StorageTreeDirectory)
            is_child_stf = isinstance(child, storage_tree.StorageTreeFile)
            if is_child_stf:
                # The child is a file
                r += f"{eol}</li>"
                r += f"<ul style=\"list-style-type: {list_styles[obj.level % len(list_styles)]}\">"
                r += child.__repr__()
                r += "</ul>"
            elif is_child_std:
                # The child is a directory.
                r += child.__repr__()
        elif len(children) > 1:
            # We have several children.
            # We want to display one on each line.
            r += f"{eol}</li>"
            r += f"<ul style=\"list-style-type: {list_styles[obj.level % len(list_styles)]}\">"
            for child in children:
                r += child.__repr__()
            r += "</ul>"

        return r

    @staticmethod
    def stf_repr(obj: storage_tree.StorageTreeFile) -> str:
        """
        :param storage_tree.StorageTreeFile obj:
        :return str:
        """
        p = obj.index / obj.nb_results
        r = f"<li><a style=\"color: rgb({int(255 - (p * 255))}, 0, 0);\">"
        if obj.index < 10:
            r += "<b>"
        r += f'<abbr title="{obj.path}">{obj.name}</abbr> | {storage_tree.human_readable_bytes(obj.size)}'
        if obj.index < 10:
            r += "</b>"
        r += f"</a></li>"
        return r

    @staticmethod
    def st_repr(obj: storage_tree.StorageTree) -> str:
        """
        :param storage_tree.StorageTree obj:
        :return str:
        """
        r = "<html>"
        r += "<body>"
        r += f"<ul style=\"list-style-type: {list_styles[1]}\">"
        r += obj.root.__repr__()
        r += "</ul>"
        r += "</body>"
        r += "</html>"
        return r


if __name__ == "__main__":
    st = storage_tree.StorageTree(storage_tree.pydu_result_file, view=View)
    st.run()
    print(st)
