import json
import re
import time

import easygui
from tqdm import tqdm

import helper

new_line_pattern = re.compile(r"\s")
clean_pattern = re.compile(r"([^'’a-zA-Z ]’?'?)")


def get_formatted_string(text: str) -> str:
    text_with_replaced_new_lines = re.sub(new_line_pattern, ' ',
                                          text.lower())  # replace new line symbols with space symbols
    result = re.sub(clean_pattern, '', text_with_replaced_new_lines)  # clear text from unwanted fragments
    result = " ".join(result.split())  # make sure that there are no double or more spaces in one place
    return result


def get_formatted_string_from_file(filename: str) -> str:
    with open(filename, 'r', errors='ignore') as file:
        file_content = file.read()

    return get_formatted_string(file_content)


def create_dictionary_json():
    file_list = easygui.fileopenbox(title='Select files for dictionary',
                                    default='*.txt', filetypes=["*.txt"], multiple=True)
    if file_list is None:
        return

    words: set = set()

    for f in tqdm(file_list, desc='Dictionary creation', unit=' files'):
        file_text = get_formatted_string_from_file(f).strip()
        words_local: set = set(file_text.split(' '))

        words |= words_local

    words_dict: dict = {"words": [w for w in words if len(w) < 15], 'symbols': list(' abcdefghijklmnopqrstuvwxyz')}

    dictionary_path = helper.get_filename_from_dialog('Select files for dictionary', '*.json', ["*.json"], False)

    with open(dictionary_path, "w") as fp:
        json.dump(words_dict, fp, indent=4)

    print(f"Total words number = {len(words_dict['words'])}")


start = time.time()
create_dictionary_json()
end = time.time()
print(f"Execution time = {end - start}")
