from tqdm import trange
from colorama import Fore

import constants


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
