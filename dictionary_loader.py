import json
import logging
import os

from tqdm import tqdm

import helper
import selection_menu
from constants import *

dictionary_data = {}  # a dictionary data container. Contains all the word and symbols statistics
dictionary_words = []
dictionary_symbols = []


def load_dictionary(dictionary_path: str) -> dict:
    """
    Loads dictionary data from specified path
    :param dictionary_path: the path to the file from which the dictionary data will be loaded
    :return: dictionary data
    """
    data = {}
    try:
        data_lines: list = []
        num_file = sum([1 for _ in open(dictionary_path, 'r')])
        with open(dictionary_path, 'r') as f:
            for idx, line in tqdm(enumerate(f), total=num_file, desc='Dictionary loading', unit='Lines',
                                  unit_scale=True):
                data_lines.append(line.strip())
        data = json.loads(''.join(data_lines))
        print(f'Dictionary loaded {Fore.GREEN}successfully{Fore.WHITE}!\n')
    except Exception as e:
        print(f'Dictionary loading {Fore.RED}failed{Fore.WHITE}! Choose another dictionary file or try again.\n')
        logging.exception(e)

    return data


def get_dictionary_path() -> str:
    """
    Shows file dialog window in which the user can select the file to load the dictionary from
    :return: path of selected file
    """
    return helper.get_filename_from_dialog('Select dictionary file', '*.json', ["*.json"])


def show_dictionary_selection_menu(**kwargs):
    """
    Shows a selection menu where the user can choose what dictionary he wants to use
    """
    global dictionary_data, dictionary_words, dictionary_symbols

    if selection_menu.choose(dictionary_menu_title, dictionary_menu_options, **kwargs) == dictionary_menu_options[0]:
        file_path = default_dictionary_path
        if not os.path.exists(default_dictionary_path):
            file_path = get_dictionary_path()
    else:
        file_path = get_dictionary_path()
    dictionary_data = load_dictionary(file_path)

    while dictionary_data == {}:
        show_dictionary_selection_menu()

    dictionary_words = dictionary_data['words']
    dictionary_symbols = dictionary_data['symbols']
