import json
import logging
import os

from tqdm import tqdm

import selection_menu
from constants import *
from helpers import helper

vocabulary_data = {}  # a vocabulary data container. Contains all the word and symbols statistics
vocabulary_words = []


# vocabulary_symbols = []


def load_vocabulary(vocabulary_path: str) -> dict:
    """
    Loads vocabulary data from specified path
    :param vocabulary_path: the path to the file from which the vocabulary data will be loaded
    :return: vocabulary data
    """
    data = {}
    try:
        f = open(vocabulary_path, 'r')
        file_lines = f.readlines()
        data_lines: list = [''] * len(file_lines)
        for idx, line in tqdm(enumerate(file_lines), total=len(file_lines), desc='Vocabulary loading', unit='Lines',
                              unit_scale=True):
            data_lines[idx] = line
        data = json.loads(''.join(data_lines))
        f.close()
        if 'words' not in data:
            raise Exception("There is no 'words' key in the loaded json file!")
        print(f'Vocabulary loaded {Fore.GREEN}successfully{Fore.WHITE}!\n')
    except Exception as e:
        print(f'Vocabulary loading {Fore.RED}failed{Fore.WHITE}! Choose another vocabulary file or try again.')
        if isinstance(e, FileNotFoundError):
            print(f"{Fore.RED}Error: {Fore.WHITE}{e.strerror}: '{e.filename}'")
        else:
            logging.exception(e)
        print()
        return {}

    return data


def get_vocabulary_path() -> str:
    """
    Shows file dialog window in which the user can select the file to load the vocabulary from
    :return: path of selected file
    """
    return helper.get_path_from_dialog('Select vocabulary file', '*.json', ["*.json"])


def show_vocabulary_selection_menu(**kwargs):
    """
    Shows a selection menu where the user can choose what vocabulary he wants to use
    """
    global vocabulary_data, vocabulary_words, vocabulary_symbols

    if selection_menu.choose(vocabulary_menu_title, vocabulary_menu_options, **kwargs) == vocabulary_menu_options[0]:
        file_path = default_vocabulary_path
        if not os.path.exists(default_vocabulary_path):
            file_path = get_vocabulary_path()
    else:
        file_path = get_vocabulary_path()
    vocabulary_data = load_vocabulary(file_path)

    if vocabulary_data == {}:
        show_vocabulary_selection_menu(**kwargs)
        return

    vocabulary_words = vocabulary_data['words']
    # vocabulary_symbols = vocabulary_data['symbols']
