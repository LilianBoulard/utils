# -*- coding: utf-8 -*-

import storage_tree


class View:

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
            r += child.__repr__()
        r += "</ul>"
        r += "</details>"
        return r

    @staticmethod
    def stf_repr(obj):
        """
        :param StorageTreeFile obj:
        :return str:
        """
        r = f"<li>{obj.name} | {storage_tree.human_readable_bytes(obj.size)}</li>"
        return r

    @staticmethod
    def st_repr(obj):
        """
        :param StorageTree obj:
        :return str:
        """
        r = "<html>"
        r += "<body>"
        r += obj.root.__repr__()
        r += "</body>"
        r += "</html>"
        return r


if __name__ == "__main__":
    st = storage_tree.StorageTree(storage_tree.pydu_result_file, view=View)
    st.run()
    print(st)
