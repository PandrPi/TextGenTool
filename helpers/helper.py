import logging
import random
from collections import Counter

import easygui
import numpy as np
from colorama import Fore
from numba import jit
from tqdm import trange

import constants
import dictionary_loader
from helpers.directory_selector import show_directory_box


@jit(fastmath=True)
def weighted_random_numpy(weights, weight_sum):
    random_weight = np.array(np.random.random() * weight_sum)
    bigger = weights.cumsum() > random_weight
    return bigger.argmax()


@jit(fastmath=True, nopython=True, boundscheck=False)
def weighted_random(weights, weight_sum):
    rnd = random.random() * weight_sum
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i


@jit(fastmath=True, nopython=True, boundscheck=False)
def weighted_random_with_etas(weights, weight_sum, etas):
    rnd = random.random() * weight_sum
    for i, w in enumerate(weights):
        rnd -= w * etas[i]
        if rnd < 0:
            return i


@jit(fastmath=True, nopython=True, boundscheck=False)
def sum_of_multiplied_weights(weights, weights_sum, eta, indices_of_one):
    pseudo_sum = weights_sum * eta
    one_minus_eta = 1.0 - eta
    for i in indices_of_one:
        pseudo_sum += weights[int(i)] * one_minus_eta

    return pseudo_sum


@jit(fastmath=True)
def get_etas_array(eta, array_size, indices_of_one) -> (np.array, np.float32):
    etas = np.empty(array_size, dtype=np.float32)
    etas.fill(eta)
    indices_number = indices_of_one.size

    if indices_number != 0:
        etas[indices_of_one] = 1.0

    return etas


def do_taylor_iteration(w_s: int, text_size: int, data_array):
    d_sizes = np.empty(text_size // w_s, dtype=np.float32)
    d_sizes.fill(0)
    for index, w_p in enumerate(range(0, (text_size // w_s) * w_s, w_s)):
        data_slice = data_array[w_p:w_p + w_s]
        test = np.bincount(data_slice)
        d_sizes[index] = np.count_nonzero(test)

    d_average = np.average(d_sizes)
    return d_average, np.std(d_sizes), w_s


def do_taylor(data_array, text_size, points_number):
    # max window size is only 5% of the text length
    max_window_size = int(text_size * 0.05)
    # starts with 10000 windows
    window_initial_size = text_size // 10000
    increment_size = int((max_window_size - window_initial_size) // (points_number - 1))

    d_sizes = np.empty(points_number, dtype=np.float32)
    std_values = np.empty(points_number, dtype=np.float32)
    w_sizes = np.empty(points_number, dtype=np.int32)

    for i, window_size in enumerate(range(window_initial_size, max_window_size, increment_size)):
        if i >= points_number:
            break
        d_sizes[i], std_values[i], w_sizes[i] = do_taylor_iteration(window_size, text_size, data_array)

    return d_sizes, std_values, w_sizes


def list_to_indices(source: list) -> list:
    """
    Converts source list to a list of equal length, in which each element is an index of a relative element of the source list
    """
    unique = {}
    item_ids = []
    for item in source:
        if item not in unique:
            unique[item] = len(unique)
        item_ids.append(unique[item])
    return item_ids


def indices_to_values(indices: list, values: list) -> list:
    """
    Converts indices list to a list of equal length, in which each element equals values[i],
    where i is the relative element of indices index
    """
    return [values[i] for i in indices]


def save_generated_text_to_file(model, generated_units: list):
    # get default filename generated from the parameters of the model and generated text
    default_filename = get_filename_from_generation_params(model.name, len(generated_units), model.parameters) + '.txt'
    # ask user to select the resulting filename in the dialog window
    filename = get_path_from_dialog('Save the generated text to file', default_filename,
                                    ["*.txt"], open_dialog=False)
    if filename != '':
        # convert indices to list of words
        words = indices_to_values(generated_units, dictionary_loader.dictionary_words)
        # save generated text to file
        write_text_to_file(filename, get_text_from_list(words))


def human_format(number: float) -> str:
    """
    Formats long number to a shorter version (Example: 1000000 -> 1M)

    :param number: The number to format
    :return: Formatted string
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


def calculate_statistics(text_units: list, heaps_points: int = 10000, taylor_points: int = 150):
    statistics_data: dict = {}

    # Heaps data
    window_position = 0
    total_world_numbers, dictionary_sizes = [], []
    word_set = set()
    increment_size: int = len(text_units) // heaps_points
    window_size: int = increment_size

    while window_size < len(text_units):
        word_set |= set(text_units[window_position:window_size])

        total_world_numbers.append(window_size)
        dictionary_sizes.append(len(word_set))

        window_size += increment_size
        window_position += increment_size
    statistics_data['heaps'] = {
        'x': total_world_numbers,
        'y': dictionary_sizes
    }

    # Zipf data
    word_frequencies = get_word_frequencies(text_units)
    statistics_data['zipf'] = {
        'x': list(range(1, len(word_frequencies) + 1)),
        'y': list(word_frequencies.values())
    }

    # Taylor data


def save_statistics(statistics_data: dict):
    pass


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


def get_path_from_dialog(title: str, default: str = '*', file_types: list = None, open_dialog: bool = True,
                         folder_mode: bool = False) -> str:
    """
    Shows the user a dialog box for selecting a file from the local drive

    :param title: A title of the dialog window
    :param default: A default filename (Example: default.txt)
    :param file_types: A list of available file extensions (Example: ['*.txt'])
    :param open_dialog: The fileopenbox method will be used if true, otherwise the filesavebox method will be used
    :param folder_mode: Will the dialog box ask user to select a folder(True) or a file(False)
    :return: Selected filename or an empty string if the user closed dialog window three times
    """
    selected_path = None
    max_closes: int = 2
    file_method = show_directory_box if folder_mode else easygui.fileopenbox if open_dialog else easygui.filesavebox
    for i in range(max_closes):
        attempts = max_closes - i
        selected_path = file_method(title=title + " ({0} attempt{1} left)".format(attempts, 's'[:attempts ^ 1]),
                                    default=default, filetypes=file_types)
        if selected_path is not None:
            break

    if selected_path is not None:
        if folder_mode is False:
            extension = file_types[0].replace('*', '')
            if selected_path.endswith(extension) is False:
                selected_path += extension
        return selected_path
    return ''
