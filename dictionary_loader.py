import json
import logging
import os

from tqdm import tqdm

from helpers import helper
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
        f = open(dictionary_path, 'r')
        file_lines = f.readlines()
        data_lines: list = [''] * len(file_lines)
        for idx, line in tqdm(enumerate(file_lines), total=len(file_lines), desc='Dictionary loading', unit='Lines',
                              unit_scale=True):
            data_lines[idx] = line
        data = json.loads(''.join(data_lines))
        f.close()
        print(f'Dictionary loaded {Fore.GREEN}successfully{Fore.WHITE}!\n')
    except Exception as e:
        print(f'Dictionary loading {Fore.RED}failed{Fore.WHITE}! Choose another dictionary file or try again.')
        if isinstance(e, FileNotFoundError):
            print(f"{Fore.RED}Error: {Fore.WHITE}{e.strerror}: '{e.filename}'")
        else:
            logging.exception(e)
        print()

    return data


def get_dictionary_path() -> str:
    """
    Shows file dialog window in which the user can select the file to load the dictionary from
    :return: path of selected file
    """
    return helper.get_path_from_dialog('Select dictionary file', '*.json', ["*.json"])


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

    if dictionary_data == {}:
        show_dictionary_selection_menu(**kwargs)
        return

    dictionary_words = dictionary_data['words']
    dictionary_symbols = dictionary_data['symbols']
