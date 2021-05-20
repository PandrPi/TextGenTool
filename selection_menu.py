import ctypes
import os
import time
from ctypes import windll, create_unicode_buffer

import keyboard
from colorama import Fore

from constants import selection_menu_additional_options
from helpers import helper


def can_handle_keyboard():
    """
    Checks whether the current process or its parent process is equal to the process whose window is the active windows
    """
    h_wnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(h_wnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(h_wnd, buf, length + 1)
    fwt = buf.value if buf.value else None

    lpdw_process_id = ctypes.c_ulong()
    windll.user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(lpdw_process_id))
    focused_process_id = lpdw_process_id.value

    return os.getpid() == focused_process_id or os.getppid() == focused_process_id or (
                fwt is not None and 'PyCharm' in fwt)


def perform_action(action):
    print(can_handle_keyboard())
    if can_handle_keyboard() is True:
        action()


def __print_option(index, option):
    print(f" {Fore.GREEN + str(index)}. {Fore.WHITE + option}")


def choose(title: str, options: list, show_turn_back: bool = True, show_start_over: bool = True) -> str:
    """
    Shows menu, where user can choose one of the presented options

    :param title: Menu title
    :param options: List of options
    :param show_turn_back: If True a 'Turn back' option will be shown
    :param show_start_over: If True a 'Start over' option will be shown
    :return: The option selected by user
    """
    selected_options = []

    print(f"{Fore.GREEN + chr(9679)} {Fore.WHITE + title}")
    for i in range(0, len(options)):
        keyboard.add_hotkey(str(i + 1), lambda index=i: perform_action(lambda: selected_options.append(options[index])))
        __print_option(i + 1, options[i])

    if show_turn_back:
        __print_option(9, selection_menu_additional_options[0])
        keyboard.add_hotkey('9', lambda: (selected_options.append(selection_menu_additional_options[0])))
    if show_start_over:
        __print_option(0, selection_menu_additional_options[1])
        keyboard.add_hotkey('0', lambda: (selected_options.append(selection_menu_additional_options[1])))

    while len(selected_options) == 0:
        time.sleep(0.1)

    print(f"You choose option '{Fore.GREEN + selected_options[0] + Fore.WHITE}'", '\n')
    keyboard.clear_all_hotkeys()
    helper.flush_input()  # we should clear input buffer
    return selected_options[0]
