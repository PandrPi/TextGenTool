import os
import random

import constants
import dictionary_loader
import helper
import parameters_menu
import plot_drawer
import selection_menu
from generation_models.general_model import GenModel
from generation_models.poisson_dirichlet_model import PoissonDirechletModel
from generation_models.polya_urn import PolyaUrn
from generation_models.polya_urn_classic import PolyaUrnClassic
from stopwatch import Stopwatch

# !!! IMPORTANT TERMINOLOGY !!!
#
# unit - generalization of word or symbol(if it will be implemented in app)
# type - unique unit
# token - duplicate of the specific type, can exist in many places in the text
#
# TO BUILD AN EXE FILE OUT OF MAIN.PY USE THE FOLLOWING COMMAND IN TERMINAL:
# pyinstaller --onefile --name TextGenTool main.py
# OR
# pyinstaller --name TextGenTool main.py

from time import time
from random import randint
from collections import Counter
from copy import deepcopy
import numpy as np
import bisect
import itertools


def weighted_random1(seq, weights, weight_sum):
    r = random.random() * weight_sum
    weights_cum = list(itertools.accumulate(weights))
    index = bisect.bisect_right(weights_cum, r)
    return seq[index]


iterations = 10000
items = list('abcde') * 500
weights = [18, 1, 1, 1, 1] * 500
total1 = 0
weights_cum1 = [total1 := (total1 + x) for x in weights]
weight_sum = sum(weights)

weights_temp = [5, 7, 4, 2, 8] * 500
weights_acc_temp = [5, 7, 4, 2, 8] * 500

test = [0, 1, 2, 3, 4]
test1 = [0, 1, 2, 3, 4, 5, 6, 7]
test[2:4] = test1[5:7]


random.seed = 0
for _ in range(100):
    index = randint(0, len(weights_temp))
    weights_temp.insert(index, randint(0, 100))

    temp1 = list(itertools.accumulate(weights_temp))

# time_sum = 0
# for _ in range(iterations):
#     start = time()
#     temp = itertools.accumulate(weights)
#     time_sum += time() - start
# print('itertools: ', time_sum)

# time_sum = 0
# for _ in range(iterations):
#     start = time()
#     total = 0
#     temp = [total := (total + x) for x in weights]
#     time_sum += time() - start
# print('list comprehensions: ', time_sum)
#
# time_sum = 0
# for _ in range(iterations):
#     start = time()
#     temp = np.cumsum(weights)
#     time_sum += time() - start
# print('np: ', time_sum)

time_sum = 0
for _ in range(iterations):
    start = time()
    temp = helper.weighted_random(items, weights, weight_sum)
    time_sum += time() - start
print(time_sum)

# print(Counter(helper.weighted_random(items, weights, weight_sum) for _ in range(iterations)))

time_sum = 0
for _ in range(iterations):
    start = time()
    temp = weighted_random1(items, weights, weight_sum)
    time_sum += time() - start
print(time_sum)

# print(Counter(weighted_random1(items, weights, weight_sum) for _ in range(iterations)))
print()

if __name__ == "__main__":
    model: GenModel
    models: list = [PolyaUrn('Polya Urn model'), PolyaUrnClassic('Classic Polya Urn model'),
                    PoissonDirechletModel('Poisson-Dirichlet model')]

    method_list = [lambda **kwargs: dictionary_loader.show_dictionary_selection_menu(**kwargs),
                   lambda **kwargs: selection_menu.choose(constants.model_selection_menu_title,
                                                          [m.name for m in models], **kwargs)]
    current_index = 0

    generated_units: list = []

    # main loop
    while 1:
        choice = method_list[current_index](show_turn_back=(current_index != 0), show_start_over=(current_index != 0))

        # turn back to previous menu
        if choice == constants.selection_menu_turn_back:
            current_index = helper.clamp(current_index - 1, 0, len(method_list) - 1)
            continue
        # start again from zeroth menu
        if choice == constants.selection_menu_start_over:
            current_index = 1
            continue

        # check whether current menu is model selection menu
        if current_index == 1:
            model = [i for i in models if i.name == choice][0]  # set the chosen model as current model
            parameters_menu.complete(model)
            print(model.parameters)
            watch1 = Stopwatch.start_new('Total time: {0} secs')
            generated_units = model.generate()
            watch1.display_time()

            plot_drawer.draw_zipf_law(helper.get_word_frequencies(generated_units))
            plot_drawer.draw_heaps_law(generated_units)

            # get default filename generated from the parameters of the model and generated text
            default_filename = helper.get_filename_from_generation_params(model.name, len(generated_units),
                                                                          model.parameters) + '.txt'
            # ask user to select the resulting filename in the dialog window
            filename = helper.get_filename_from_dialog('Save the generated text to file', default_filename,
                                                       ["*.txt"], open_dialog=False)
            if filename != '':
                # save generated text to file
                helper.write_text_to_file(filename, helper.get_text_from_list(generated_units))

        current_index = helper.clamp(current_index + 1, 0, len(method_list) - 1)

    os.system("pause")
