import logging
from collections import Counter

import easygui
from colorama import Fore
from tqdm import trange

import constants


def human_format(number: float) -> str:
    """
    Formats long number to a shorter version (Example: 1000000 -> 1M)
    :param number: The number to format
    :return:
    """
    number = float('{:.3g}'.format(number))
    magnitude = 0
    while abs(number) >= 1000:
        magnitude += 1
        number /= 1000.0
    return '{}{}'.format('{:f}'.format(number).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def get_filename_from_generation_params(model_name: str, text_length: int, parameters: dict) -> str:
    result: str = model_name.lower().replace(' model', '').replace(' ', '_')
    result += f"__text_length[{human_format(text_length)}]"
    for k, v in parameters.items():
        if k == 'text_length' or k == 'urn_initial_size':
            continue
        result += "_{0}[{1}]".format(k, v['value'])

    return result


def write_text_to_file(filename: str, text: str):
    try:
        with open(filename, "w") as fp:
            fp.write(text)
    except Exception as e:
        logging.exception(e)


def read_text_file(filename: str) -> str:
    with open(filename, 'r', errors='ignore') as file:
        return file.read().strip()


def get_word_frequencies(word_list: list) -> dict:
    """
    Calculates the number of occurrences of all the words in the specified list
    :param word_list: A list of words
    :return: A sorted word frequency dictionary
    """
    return dict(Counter(word_list).most_common())


def clamp(value, min_limit, max_limit):
    return max(min_limit, min(value, max_limit))


def get_text_from_list(units: list) -> str:
    """
    Converts a list of units to a single string where units are separated by spaces
    :param units: List of units
    :return: Text string
    """
    return ' '.join(units)


def model_range(*args, **kwargs):
    kwargs['desc'] = constants.model_generation_format.format(kwargs['desc'])
    kwargs['unit'] = 'Units'
    kwargs['unit_scale'] = True
    return trange(*args, **kwargs)


def print_type_container_is_empty_message(desired_text_length, text_length):
    print(f"\n{Fore.YELLOW}IMPORTANT{Fore.WHITE}: Cannot reach desired text length, the dictionary is empty.\n"
          f"Generated text length is {text_length}/{desired_text_length} units. Choose smaller text size or try again.")


def flush_input():
    """
    Clears all the pressed keys from the input buffer
    """
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios  # for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


def safe_cast(value, to_type, default=None):
    """
    Safe value casting to desired type
    :param value: Value to cast
    :param to_type: Desired value's type
    :param default: Value which is returned if cast failed
    :return: Converted value
    """
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default


def get_filename_from_dialog(title: str, default: str, file_types: list, open_dialog: bool = True) -> str:
    """
    Shows the user a dialog box for selecting a file from the local drive
    :param title: A title of the dialog window
    :param default: A default filename (Example: default.txt)
    :param file_types: A list of available file extensions (Example: ['*.txt'])
    :param open_dialog: The fileopenbox method will be used if true, otherwise the filesavebox method will be used
    :return: Selected filename or an empty string if the user closed dialog window three times
    """
    filename = None
    max_closes: int = 3
    for i in range(max_closes):
        if open_dialog:
            filename = easygui.fileopenbox(title=title, default=default, filetypes=file_types)
        else:
            filename = easygui.filesavebox(title=title, default=default, filetypes=file_types)
        if filename is not None:
            break

    if i != max_closes - 1:
        extension = file_types[0].replace('*', '')
        if not filename.endswith(extension):
            filename += extension
        return filename
    return ''
