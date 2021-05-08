import os

import dictionary_loader
import parameters_menu
import selection_menu
from constants import *
from generation_models.general_model import GenModel
from generation_models.poisson_dirichlet_model import PoissonDirechletModel
from generation_models.polya_urn import PolyaUrn
from generation_models.polya_urn_classic import PolyaUrnClassic
from generation_models.semantics_poisson_dirichlet_model import PoissonDirechletModelWithSemantics
from generation_models.semantics_polya_urn import PolyaUrnWithSemantics
from helpers import helper, plot_drawer
from helpers.stopwatch import Stopwatch

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


if __name__ == "__main__":

    # # filename = helper.get_path_from_dialog('test', '*.txt', file_types=['*.txt'])
    # # filename = 'C:\\Users\\Andrushko\\Desktop\\my texts\\+lotr_en.txt'
    # filename = 'C:\\Users\\Andrushko\\Desktop\\polya_urn__text_length[1M]_rho[2]_nu[1].txt'
    # words = []
    #
    # with open(filename, 'r', encoding='utf8') as f:
    #     for i in f.readlines():
    #         words += i.split(' ')
    #
    # watch = Stopwatch.start_new('Time: {0} secs')
    # plot_drawer.draw_taylor_law(helper.list_to_indices(words), {'rho': 5}, 100)
    # watch.display_time()

    model: GenModel
    models: list = [
        PolyaUrn('Polya Urn model'),
        PolyaUrnClassic('Classic Polya Urn model'),
        PoissonDirechletModel('Poisson-Dirichlet model'),
        PolyaUrnWithSemantics('Polya Urn model with semantics'),
        PoissonDirechletModelWithSemantics('Poisson-Dirichlet model with semantics'),
    ]

    menu_method_list = [
        lambda **kwargs: dictionary_loader.show_dictionary_selection_menu(**kwargs),
        lambda **kwargs: selection_menu.choose(model_selection_menu_title, [m.name for m in models], **kwargs),
        lambda **kwargs: selection_menu.choose(analysis_menu_title, analysis_menu_options, **kwargs)
    ]

    current_index = 0
    generated_units: list = []
    statistics_data: dict = {}

    text_analysis_methods = [
        lambda: plot_drawer.draw_zipf_law(helper.get_word_frequencies(generated_units), model.get_params_for_plot()),
        lambda: plot_drawer.draw_heaps_law(generated_units, model.get_params_for_plot()),
        lambda: plot_drawer.draw_taylor_law(helper.list_to_indices(generated_units), model.get_params_for_plot()),
        lambda: helper.save_statistics(statistics_data),
        lambda: helper.save_generated_text_to_file(model, generated_units)
    ]

    # main loop
    while 1:
        choice = menu_method_list[current_index](show_turn_back=(current_index != 0),
                                                 show_start_over=(current_index != 0))

        # turn back to previous menu
        if choice == selection_menu_turn_back:
            current_index = helper.clamp(current_index - 1, 0, len(menu_method_list) - 1)
            continue
        # start again from zeroth menu
        if choice == selection_menu_start_over:
            current_index = 1
            continue

        # check weather the current menu is a model selection menu
        if current_index == 1:
            model = [i for i in models if i.name == choice][0]  # set the chosen model as current model
            parameters_menu.complete(model)
            watch1 = Stopwatch.start_new('Total time: {0} secs\n')
            generated_units = model.generate()
            watch1.display_time()
            # helper.calculate_statistics(generated_units)

        # check weather the current menu is a text analysis menu
        if current_index == 2:
            analysis_method = text_analysis_methods[analysis_menu_options.index(choice)]
            analysis_method()

        current_index = helper.clamp(current_index + 1, 0, len(menu_method_list) - 1)

    os.system("pause")
