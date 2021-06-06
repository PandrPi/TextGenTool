import concurrent
import logging
import math
import random
import re
from collections import Counter
from concurrent.futures.thread import ThreadPoolExecutor
from os import path

import easygui
import numpy as np
from colorama import Fore
from numba import jit
from tqdm import trange

import constants
import vocabulary_loader
from helpers.path_selector import show_directory_box, show_file_open_box
from helpers.settings_helper import Settings
from helpers.stopwatch import Stopwatch


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


def show_welcome_message(models: list):
    white, green, yellow = Fore.WHITE, Fore.GREEN, Fore.YELLOW
    print('{0}!!!{1} Welcome to the TextGenTool  {0}!!!{2}\n'.format(yellow, green, white))

    print('Sliding window parameters:')
    points_number = Settings.get_value('sliding_window_points_number')
    print('\t{2}{0}{3} = {4}{1}{3}'.format('Points number', points_number, green, white, yellow))
    window_step_divider = Settings.get_value('sliding_window_step_divider')
    print('\t{2}{0}{3} = {4}{1}{3}'.format('Window step divider', window_step_divider, green, white, yellow))

    print('\nThere are the short names of the models presented below:')
    for i in models:
        print('\t{2}{0}{3} -> {4}{1}{3}'.format(i.short_name, i.name, green, white, yellow))

    print()


def get_units_from_external_text_file() -> (list, str):
    clean_pattern1 = re.compile(r"([^'’a-zA-Z- ])|([\s]{2,})")
    clean_pattern2 = re.compile(r"([\s]+)")

    filename = get_path_from_dialog('Select text file', default='*.txt', file_types=["*.txt"])
    if filename == '':
        print(f"{Fore.RED}Failed{Fore.WHITE} to load text file! Try again or choose another option in the menu.\n")
        return [], ''

    try:
        text = read_text_file(filename)
        if isinstance(text, Exception):
            raise text
        text = re.sub(clean_pattern1, ' ', text)
        text = re.sub(clean_pattern2, ' ', text).strip()
        units = text.split(' ')
    except Exception as e:
        logging.exception(e)
        return [], ''

    return units, filename


def perform_taylor_law_calculation(action, data_array, text_size, points_number, window_initial_size, max_window_size,
                                   increment_size):
    window_step_divider = Settings.get_value('sliding_window_step_divider')
    arguments, result_list = [], []
    for i, window_size in enumerate(range(window_initial_size, max_window_size, increment_size)):
        if i >= points_number:
            break
        arguments.append([window_size, text_size, data_array, window_step_divider])

    futures = []
    with ThreadPoolExecutor() as executor:
        for args_local in arguments:
            futures.append(executor.submit(action, *args_local))

    futures, _ = concurrent.futures.wait(futures)
    for i, future in enumerate(futures):
        result_list.append(future.result())

    return result_list


def create_sliding_window_params(text_limit_coefficient: float, text_size: int, points_number):
    max_window_size = int(text_size * text_limit_coefficient)
    # starts with 10000 windows, but if text_size is smaller then initial size of window will be 10
    window_initial_size = max(text_size // 10000, 10)
    points_number = min(points_number, max_window_size - window_initial_size)
    increment_size = int((max_window_size - window_initial_size) // (points_number - 1))

    return max_window_size, window_initial_size, points_number, increment_size


def do_taylor_iteration_dynamic(w_s: int, text_size: int, data_array, window_step_divider: int):
    points_number = math.ceil(((text_size // w_s) * w_s - w_s) / (w_s // window_step_divider))
    d_sizes = np.empty(points_number, dtype=np.float32)
    d_sizes.fill(0)

    for index, w_p in enumerate(range(0, (text_size // w_s) * w_s - w_s, w_s // window_step_divider)):
        data_slice = data_array[w_p:w_p + w_s]
        d_sizes[index] = np.unique(data_slice).size
    d_average = np.average(d_sizes)
    return d_average, np.std(d_sizes), w_s


def do_taylor_dynamic(data_array, text_size, points_number):
    # max window size is only 5% of the text length, so text_limit_coefficient should be equal 0.05
    max_window_size, window_initial_size, points_number, increment_size = create_sliding_window_params(0.05, text_size,
                                                                                                       points_number)

    d_sizes = np.empty(points_number, dtype=np.float32)
    std_values = np.empty(points_number, dtype=np.float32)
    w_sizes = np.empty(points_number, dtype=np.int32)

    result = perform_taylor_law_calculation(do_taylor_iteration_dynamic, data_array, text_size, points_number,
                                            window_initial_size,
                                            max_window_size, increment_size)

    for i, value in enumerate(result):
        d_sizes[i], std_values[i], w_sizes[i] = value

    return d_sizes, std_values, w_sizes


def do_taylor_iteration_static(w_s: int, text_size: int, data_array, window_step_divider: int):
    points_number = math.ceil(((text_size // w_s) * w_s - w_s) / (w_s // window_step_divider))
    d_sizes = np.empty(points_number, dtype=np.float32)
    d_sizes.fill(0)

    for index, w_p in enumerate(range(0, (text_size // w_s) * w_s - w_s, w_s // window_step_divider)):
        data_slice = data_array[w_p:w_p + w_s]
        d_sizes[index] = np.count_nonzero(data_slice)
    d_average = np.average(d_sizes)
    return d_average, np.std(d_sizes), w_s


def do_taylor_static(data_array, text_size, points_number):
    _, unique_indices = np.unique(data_array, return_index=True)
    unique_mask = np.empty(text_size, dtype=np.int32)
    unique_mask.fill(0)
    unique_mask[unique_indices] = 1

    # max window size is only 5% of the text length, so text_limit_coefficient should be equal 0.05
    max_window_size, window_initial_size, points_number, increment_size = create_sliding_window_params(0.05, text_size,
                                                                                                       points_number)

    d_sizes = np.empty(points_number, dtype=np.float32)
    std_values = np.empty(points_number, dtype=np.float32)
    w_sizes = np.empty(points_number, dtype=np.int32)

    result = perform_taylor_law_calculation(do_taylor_iteration_static, unique_mask, text_size, points_number,
                                            window_initial_size,
                                            max_window_size, increment_size)

    for i, value in enumerate(result):
        d_sizes[i], std_values[i], w_sizes[i] = value

    return d_sizes, std_values, w_sizes


def do_heaps_iteration_dynamic(w_s: int, data_array):
    data_slice = data_array[0:w_s]
    return np.unique(data_slice).size, w_s


def do_heaps_dynamic(data_array, text_size, points_number):
    # max window size equals text_length, so text_limit_coefficient should be equal 1.0
    max_window_size, window_initial_size, points_number, increment_size = create_sliding_window_params(1.0, text_size,
                                                                                                       points_number)

    d_sizes = np.empty(points_number, dtype=np.float32)
    w_sizes = np.empty(points_number, dtype=np.int32)

    arguments = []
    for i, window_size in enumerate(range(window_initial_size, max_window_size, increment_size)):
        if i >= points_number:
            break
        arguments.append([window_size, data_array])

    futures = []
    with ThreadPoolExecutor() as executor:
        for args_local in arguments:
            futures.append(executor.submit(do_heaps_iteration_dynamic, *args_local))

    futures, _ = concurrent.futures.wait(futures)
    for i, future in enumerate(futures):
        d_sizes[i], w_sizes[i] = future.result()

    return d_sizes, w_sizes


def do_heaps_iteration_static(w_s: int, data_array):
    data_slice = data_array[0:w_s]
    return np.count_nonzero(data_slice), w_s


def do_heaps_static(data_array, text_size, points_number):
    _, unique_indices = np.unique(data_array, return_index=True)
    unique_mask = np.empty(text_size, dtype=np.int32)
    unique_mask.fill(0)
    unique_mask[unique_indices] = 1

    # max window size equals text_length, so text_limit_coefficient should be equal 1.0
    max_window_size, window_initial_size, points_number, increment_size = create_sliding_window_params(1.0, text_size,
                                                                                                       points_number)

    d_sizes = np.empty(points_number, dtype=np.float32)
    w_sizes = np.empty(points_number, dtype=np.int32)

    arguments = []
    for i, window_size in enumerate(range(window_initial_size, max_window_size, increment_size)):
        if i >= points_number:
            break
        arguments.append([window_size, unique_mask])

    futures = []
    with ThreadPoolExecutor() as executor:
        for args_local in arguments:
            futures.append(executor.submit(do_heaps_iteration_static, *args_local))

    futures, _ = concurrent.futures.wait(futures)
    for i, future in enumerate(futures):
        d_sizes[i], w_sizes[i] = future.result()

    return d_sizes, w_sizes


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


def save_generated_text_to_file(model, generated_units: list, external_filename: str):
    if external_filename == '':
        # get default filename generated from the parameters of the model and generated text
        default_filename = get_filename_from_model_params(model.short_name, len(generated_units), model.parameters)
    else:
        default_filename = external_filename
    # ask user to select the resulting filename in the dialog window
    filename = get_path_from_dialog('Save the generated text to file', default_filename, ["*.txt"], open_dialog=False)
    if filename == '':
        print(f"{Fore.RED}Failed{Fore.WHITE} to save the text file! Try again or choose another option in the menu.\n")
        return False

    if external_filename == '':
        # convert indices to list of words
        words = indices_to_values(generated_units, vocabulary_loader.vocabulary_words)
    else:
        words = generated_units
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


def get_filename_from_model_params(model_name: str, text_length: int, parameters: dict) -> str:
    result: str = model_name.replace(' model', '').replace(' ', '_')
    result += f"__[{human_format(text_length)}]"
    for k, v in parameters.items():
        if k == 'text_length' or k == 'urn_initial_size':
            continue
        result += "_{0}[{1}]".format(k, v['value'])

    return result + '.txt'


def write_text_to_file(filename: str, text: str):
    try:
        with open(filename, "w") as fp:
            fp.write(text)
    except Exception as e:
        logging.exception(e)


def read_text_file(filename: str) -> str:
    try:
        with open(filename, 'r', errors='ignore') as file:
            return file.read().strip()
    except Exception as e:
        logging.exception(e)
        return e


def get_word_frequencies(word_list: list) -> dict:
    """
    Calculates the number of occurrences of all the words in the specified list

    :param word_list: A list of words
    :return: A sorted word frequency dictionary
    """
    return dict(Counter(word_list).most_common())


def calculate_statistics(data: list, use_static_definition: bool, points_number: int):
    print('{0}Calculating text statistics...{1}'.format(Fore.YELLOW, Fore.WHITE))
    watch = Stopwatch.start_new()
    watch.display_format = '{0}Text statistics calculated in {1}{{0}}{2} seconds!{3}\n'.format(Fore.YELLOW, Fore.GREEN,
                                                                                               Fore.YELLOW, Fore.WHITE)
    statistics_data: dict = {}

    # Taylor data
    text_size = len(data)
    word_array = np.asarray(data)
    taylor_method = do_taylor_static if use_static_definition else do_taylor_dynamic
    vocabulary_sizes, std_values, window_sizes = taylor_method(word_array, text_size, points_number)
    statistics_data['taylor'] = {
        'x': vocabulary_sizes,
        'y': std_values
    }

    # Fluctuation data
    statistics_data['fluctuation'] = {
        'x': window_sizes,
        'y': std_values
    }

    # Heaps data
    heaps_method = do_heaps_static if use_static_definition else do_heaps_dynamic
    heaps_y, heaps_x = heaps_method(word_array, text_size, points_number)
    statistics_data['heaps'] = {
        'x': heaps_x,
        'y': heaps_y
    }

    # Zipf data
    word_frequencies = get_word_frequencies(data)
    statistics_data['zipf'] = {
        'x': np.array(range(1, len(word_frequencies) + 1)),
        'y': np.array([*word_frequencies.values()])
    }

    watch.display_time()
    return statistics_data


def save_statistics(statistics_data: dict):
    folder_path: str = get_path_from_dialog('Select folder where statistics data fill be saved', folder_mode=True)

    if folder_path == '':
        print(f"{Fore.RED}Failed{Fore.WHITE} to save statistics! Try again or choose another option in the menu.\n")
        return False

    zipf_filename = path.join(folder_path, 'zipf_data.txt')
    taylor_filename = path.join(folder_path, 'taylor_data.txt')
    heaps_filename = path.join(folder_path, 'heaps_data.txt')

    zipf_data = statistics_data['zipf']
    matrix_data = np.asarray([zipf_data['x'], zipf_data['y']]).T
    np.savetxt(zipf_filename, matrix_data, delimiter="\t", fmt='%e', header='Rank\t\tFrequency')

    taylor_data = statistics_data['taylor']
    fluctuation_data = statistics_data['taylor']
    matrix_data = np.asarray([fluctuation_data['x'], taylor_data['x'], taylor_data['y']]).T
    np.savetxt(taylor_filename, matrix_data, delimiter="\t", fmt='%e', header='Windows\t\tVocabulary\tStdValues')

    heaps_data = statistics_data['heaps']
    matrix_data = np.asarray([heaps_data['x'], heaps_data['y']]).T
    np.savetxt(heaps_filename, matrix_data, delimiter="\t", fmt='%e', header='Words\t\tVocabulary')


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
    print(f"\n{Fore.YELLOW}IMPORTANT{Fore.WHITE}: Cannot reach desired text length, the vocabulary is empty.\n"
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


def get_path_from_settings_by_extension(key: str, extension: str = ''):
    value = Settings.get_value(key)
    if extension not in value:
        return None
    return value[extension]


def set_path_in_settings_by_extension(key: str, value, extension: str = ''):
    value_local = Settings.get_value(key)
    value_local[extension] = value
    Settings.set_value(key, value_local)


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

    settings_key = 'last_opened_folder' if folder_mode else 'last_opened_file' if open_dialog else 'last_saved_file'
    file_method = show_directory_box if folder_mode else show_file_open_box if open_dialog else easygui.filesavebox
    extension = '' if file_types is None else file_types[0].replace('*', '')
    default_local = get_path_from_settings_by_extension(settings_key, extension)

    # if there exist path by extension in the settings and this method is not called to save the generated text
    if default_local is not None:
        if title != 'Save the generated text to file':
            default = default_local
        else:
            temp_folder = path.split(default_local)[0]
            default = path.join(temp_folder, default)

    for i in range(max_closes):
        attempts = max_closes - i
        title_local = title + " ({0} attempt{1} left)".format(attempts, 's'[:attempts ^ 1])
        selected_path = file_method(title=title_local, default=default, filetypes=file_types)
        if selected_path is not None:
            break

    if selected_path is not None:
        if folder_mode is False:
            extension = file_types[0].replace('*', '')
            if selected_path.endswith(extension) is False:
                selected_path += extension
        else:
            extension = ''
        set_path_in_settings_by_extension(settings_key, selected_path, extension)
        return selected_path
    return ''
