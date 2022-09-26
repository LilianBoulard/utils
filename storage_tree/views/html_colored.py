# -*- coding: utf-8 -*-

from dataclasses import dataclass

from .base import BaseView, human_readable_bytes

list_styles = ['disc', 'circle', 'square']


@dataclass
class LeftoverChild:

    """
    A LeftoverChild is a dummy object used to display "..."
    when there are many files with insignificant sizes: we want to
    avoid overloading the tree display.
    """

    path: str
    name: str
    size: int
    index: int
    nb_results: int


class View(BaseView):

    @staticmethod
    def std_repr(obj) -> str:
        """
        :param storage_tree.StorageTreeDirectory obj:
        :return str:
        """
        parent = obj.parent
        children = obj.children

        is_parent_st = hasattr(parent, 'root')  # Check whether it is of type StorageTree

        if is_parent_st:
            siblings = 0
        else:
            siblings = len(parent.children) - 1

        r = ""  # This is the value that we will return (that will be printed).

        if is_parent_st:
            r += "<li>"

        if siblings == 0:
            r += f"{obj.name}/"
        elif siblings > 0:
            r += f"<li>{obj.name}/"

        # Additional value that can be added at the end of every directory line.
        eol = f" ({human_readable_bytes(obj.size)})"

        if len(children) == 1:
            # If we have only one child.
            # We skip the display thre verification because, as there is only one child,
            # it automatically represents 100% of the parent's size.
            child = children[0]
            is_child_std = hasattr(child, 'children')  # Check whether it is of type StorageTreeDirectory
            is_child_stf = hasattr(child, 'index')  # Check whether it is of type StorageTreeFile
            if is_child_stf:
                # The child is a file
                r += f"{eol}</li>"
                r += f"<ul style=\"list-style-type: {list_styles[obj.level % len(list_styles)]}\">"
                r += repr(child)
                r += "</ul>"
            elif is_child_std:
                # The child is a directory.
                r += repr(child)
        elif len(children) > 1:
            # We have several children.
            # We want to display one on each line,
            # and stop at the child which is less than `x` percent of the directory's size.
            display_threshold = obj.size * 0.01  # 0.1 = 10%
            r += f"{eol}</li>"
            r += f"<ul style=\"list-style-type: {list_styles[obj.level % len(list_styles)]}\">"
            leftover_children_size = 0
            for child in children:
                if child.size < display_threshold:
                    leftover_children_size += child.size
                else:
                    r += repr(child)
            else:
                if leftover_children_size > 0:
                    dummy_obj = LeftoverChild(path="", name="...", size=leftover_children_size,
                                              index=obj.nb_results, nb_results=obj.nb_results)
                    r += View.stf_repr(dummy_obj)  # Dirty hack
            r += "</ul>"

        return r

    @staticmethod
    def stf_repr(obj) -> str:
        """
        :param storage_tree.StorageTreeFile obj:
        :return str:
        """
        p = obj.index / obj.nb_results
        r = f"<li><a style=\"color: rgb({int(255 - (p * 255))}, 0, 0);\">"
        if obj.index < 10:  # If the index is in the top 10 of the most heavy files, we bold the text.
            r += "<b>"
        r += f'<abbr title="{obj.path}">{obj.name}</abbr> | {human_readable_bytes(obj.size)}'
        if obj.index < 10:
            r += "</b>"
        r += f"</a></li>"
        return r

    @staticmethod
    def st_repr(obj) -> str:
        """
        :param storage_tree.StorageTree obj:
        :return str:
        """
        r = "<html>"
        r += "<body>"
        r += f"<ul style=\"list-style-type: {list_styles[1]}\">"
        r += repr(obj.root)
        r += "</ul>"
        r += "</body>"
        r += "</html>"
        return r
