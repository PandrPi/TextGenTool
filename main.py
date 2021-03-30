import os

import constants
import dictionary_loader
import helper
import parameters_menu
import selection_menu
from generation_models.general_model import GenModel
from generation_models.polya_urn_classic import PolyaUrnClassic
from stopwatch import Stopwatch
from generation_models.polya_urn import PolyaUrn

# !!! IMPORTANT TERMINOLOGY !!!
#
# unit - generalization of word or symbol
# type - unique unit
# token - duplicate of the specific type, can exist in many places in the text
#

# TO BUILD AN EXE FILE OUT OF MAIN.PY USE THE FOLLOWING COMMAND IN TERMINAL:
# pyinstaller --onefile --name TextGenTool main.py


if __name__ == "__main__":
    model: GenModel
    models: list = [PolyaUrn('Polya Urn model'), PolyaUrnClassic('Classic Polya Urn model')]

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

        # check whether current menu equals model selection menu
        if current_index == 1:
            model = [i for i in models if i.name == choice][0]  # set chosen model as current model
            parameters_menu.complete(model)
            print(model.parameters)
            watch1 = Stopwatch.start_new('Total time: {0} secs')
            generated_units = model.generate()
            watch1.display_time()

        current_index = helper.clamp(current_index + 1, 0, len(method_list) - 1)

    os.system("pause")
