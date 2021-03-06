import re
import json
import time
import easygui
from tqdm import tqdm
from collections import Counter

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

    words_dict: dict = {'words_number': 0, 'words': {}, 'symbols_number': 0, 'symbols': {}}
    words = Counter(words_dict['words'])
    symbols = Counter(words_dict['symbols'])
    total_words_number = 0

    for f in tqdm(file_list, desc='Dictionary creation', unit=' files'):
        file_text = get_formatted_string_from_file(f).strip()
        word_list: list = file_text.split(' ')
        total_words_number += len(word_list)

        words += Counter(word_list)
        symbols += Counter(file_text)

    words_dict['words_number'] = total_words_number
    words_dict['words'] = dict(words)
    sorted_tuples = sorted(words_dict['words'].items(), key=lambda item: item[1], reverse=True)
    words_dict['words'] = {k: v for k, v in sorted_tuples}

    words_dict['symbols'] = dict(symbols)
    words_dict['symbols_number'] = sum(words_dict['symbols'].values())
    sorted_tuples = sorted(words_dict['symbols'].items(), key=lambda item: item[1], reverse=True)
    words_dict['symbols'] = {k: v for k, v in sorted_tuples}

    dictionary_path = None
    while dictionary_path is None:
        dictionary_path = easygui.filesavebox(title='Select files for dictionary',
                                              default='*.json', filetypes=["*.json"])
    if not dictionary_path.endswith('.json'):
        dictionary_path += '.json'
    with open(dictionary_path, "w") as fp:
        json.dump(words_dict, fp, indent=4)

    print(f'Total words number = {total_words_number}')


start = time.time()
create_dictionary_json()
end = time.time()
print(f"Execution time = {end - start}")
