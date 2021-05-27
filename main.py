import os

import parameters_menu
import selection_menu
import vocabulary_loader
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
# pyinstaller --noconfirm --name TextGenTool main.py


if __name__ == "__main__":
    # we need to initialize or model with some value or None
    model: GenModel = GenModel('Default not implemented model', {})
    models: list = [
        PolyaUrn('Polya Urn model'),
        PolyaUrnClassic('Classic Polya Urn model'),
        PoissonDirechletModel('Poisson-Dirichlet model'),
        PolyaUrnWithSemantics('Polya Urn model with semantics'),
        PoissonDirechletModelWithSemantics('Poisson-Dirichlet model with semantics'),
    ]

    external_filename: str = ''
    open_external_file_title = 'Open an external text file from storage'
    model_selection_menu_options = [m.name for m in models] + [open_external_file_title]

    menu_method_list = [
        lambda **kwargs: vocabulary_loader.show_vocabulary_selection_menu(**kwargs),
        lambda **kwargs: selection_menu.choose(model_selection_menu_title, model_selection_menu_options, **kwargs),
        lambda **kwargs: selection_menu.choose(analysis_menu_title, analysis_menu_options, **kwargs)
    ]

    current_index = 0
    generated_units: list = []
    statistics_data: dict = {}

    text_analysis_methods = [
        lambda: plot_drawer.draw_zipf_law(statistics_data['zipf'], model, external_filename),
        lambda: plot_drawer.draw_heaps_law(statistics_data['heaps'], model, external_filename),
        lambda: plot_drawer.draw_taylor_law(statistics_data['taylor'], model, external_filename),
        lambda: plot_drawer.draw_all_laws(statistics_data, model, external_filename),
        lambda: helper.save_statistics(statistics_data),
        lambda: helper.save_generated_text_to_file(model, generated_units, external_filename)
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
            if choice == open_external_file_title:
                # open an external text file
                generated_units, external_filename = helper.get_units_from_external_text_file()
            else:
                model = [i for i in models if i.name == choice][0]  # set the chosen model as current model
                external_filename = ''
                parameters_menu.complete(model)
                watch1 = Stopwatch.start_new('Total time: {0} secs\n')
                generated_units = model.generate()  # generate text by model
                watch1.display_time()

            if len(generated_units) != 0:
                statistics_data = helper.calculate_statistics(helper.list_to_indices(generated_units),
                                                              taylor_points=200)

        # check weather the current menu is a text analysis menu
        if current_index == 2:
            analysis_method = text_analysis_methods[analysis_menu_options.index(choice)]
            analysis_method()

        current_index = helper.clamp(current_index + 1, 0, len(menu_method_list) - 1)

    os.system("pause")
