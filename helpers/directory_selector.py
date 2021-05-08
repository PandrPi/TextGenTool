import os

import easygui.boxes.fileboxsetup as fbs
import easygui.boxes.utils as ut

tk = ut.tk


def show_directory_box(msg=None, title=None, default='*', **kwargs):
    """
    Displays an "select folder" dialog box and returns the selected folder as a string.


    :param str msg: the msg to be displayed.
    :param str title: the window title
    :param str default: filepath with wildcards
    :return: the name of a file, or None if user chose to cancel
    """
    local_root = tk.Tk()
    local_root.lift()
    local_root.attributes('-topmost', True)
    local_root.withdraw()

    initial_base, initial_file, initial_dir, file_types = fbs.fileboxSetup(default, None)

    ret_val = ut.tk_FileDialog.askdirectory(parent=local_root, title=ut.getFileDialogTitle(msg, title),
                                            initialdir=initial_dir)
    if not ret_val or ret_val == '':
        local_root.destroy()
        return None
    else:
        try:
            f = os.path.normpath(ret_val)
        except AttributeError as e:
            print("ret_val is {}".format(ret_val))
            raise e
    local_root.destroy()

    if not f:
        return None
    return f
