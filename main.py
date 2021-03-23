import os

import dictionary_loader
import helper
import parameters_menu
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
    dictionary_loader.show_dictionary_selection_menu()

    parameters = {
        'rho': {
            'value': 4,
            'type': int,
            'constant': False
        },
        'nu': {
            'value': 4,
            'type': int,
            'constant': False
        },
        'urn_initial_size': {
            'value': 500,
            'type': int,
            'constant': False
        },
        'text_length': {
            'value': 150000,
            'type': int,
            'constant': False
        }
    }

    watch1 = Stopwatch.start_new('Total time: {0} secs')

    # urn = PolyaUrn('Polya Urn')
    # out_list: list = urn.generate()

    parameters_menu.complete('Enter Polya Urn parameters:', parameters)
    print(parameters)

    watch1.display_time()
    # print(helper.get_text_from_list(out_list[:1000]))

    os.system("pause")
