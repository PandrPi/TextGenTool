import json
import os
import easygui
import selection_menu

from colorama import Fore
from tqdm import tqdm
from constants import *


def load_dictionary(dictionary_path: str) -> dict:
    data_str: str = ''
    num_file = sum([1 for i in open(dictionary_path, 'r')])
    with open(dictionary_path, 'r') as f:
        for idx, line in tqdm(enumerate(f), total=num_file, desc='Dictionary loading'):
            data_str += line.strip()
    data = json.loads(data_str)
    print(f'Dictionary loaded {Fore.GREEN}successfully{Fore.WHITE}!')

    return data


def choose_dictionary_file() -> str:
    filename = None
    while filename is None:
        filename = easygui.fileopenbox(title='Select dictionary file', default='*.json', filetypes=["*.json"])

    return filename


def choose_dictionary():
    if selection_menu.choose(dictionary_to_use_title, dictionary_to_use_options) == dictionary_to_use_options[0]:
        file_path: str = default_dictionary_path
        if not os.path.exists(default_dictionary_path):
            file_path = choose_dictionary_file()
        load_dictionary(file_path)
    else:
        file_path = choose_dictionary_file()
        load_dictionary(file_path)
