import json
import re
import time

import easygui
from tqdm import tqdm

from helpers import helper

clean_pattern1 = re.compile(r"([^'’a-zA-Z- ])|([\s]{2,})")
clean_pattern2 = re.compile(r"([\s]+)")


def get_formatted_string(text: str) -> str:
    result = re.sub(clean_pattern1, ' ', text.lower())  # replace unwanted fragments with space symbols
    result = re.sub(clean_pattern2, ' ', result)  # make sure that there are no double or more spaces in one place
    return result.strip()


def get_formatted_string_from_file(filename: str) -> str:
    with open(filename, 'r', errors='ignore') as file:
        file_content = file.read()

    return get_formatted_string(file_content)


def create_vocabulary_json():
    file_list = easygui.fileopenbox(title='Select files for vocabulary',
                                    default='*.txt', filetypes=["*.txt"], multiple=True)
    if file_list is None:
        return

    words: set = set()

    for f in tqdm(file_list, desc='Vocabulary creation', unit=' files'):
        file_text = get_formatted_string_from_file(f).strip()
        words_local: set = set(file_text.split(' '))

        words |= words_local

    words_dict: dict = {"words": [w for w in words if len(w) < 15], 'symbols': list(' abcdefghijklmnopqrstuvwxyz')}

    vocabulary_path = helper.get_path_from_dialog('Select files for vocabulary', '*.json', ["*.json"], False)

    with open(vocabulary_path, "w") as fp:
        json.dump(words_dict, fp, indent=4)

    print(f"Total words number = {len(words_dict['words'])}")


start = time.time()
create_vocabulary_json()
end = time.time()
print(f"Execution time = {end - start}")
