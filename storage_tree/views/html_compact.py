# -*- coding: utf-8 -*-

from .base import BaseView, human_readable_bytes


class View(BaseView):

    @staticmethod
    def std_repr(obj):
        """
        :param StorageTreeDirectory obj:
        :return str:
        """
        r = "<details>"
        r += "<summary>"
        r += f"{obj.name}/"
        r += "</summary>"
        r = "<ul>"
        for child in obj.children:
            r += repr(child)
        r += "</ul>"
        r += "</details>"
        return r

    @staticmethod
    def stf_repr(obj):
        """
        :param StorageTreeFile obj:
        :return str:
        """
        r = f"<li>{obj.name} | {human_readable_bytes(obj.size)}</li>"
        return r

    @staticmethod
    def st_repr(obj):
        """
        :param StorageTree obj:
        :return str:
        """
        r = "<html>"
        r += "<body>"
        r += repr(obj.root)
        r += "</body>"
        r += "</html>"
        return r
