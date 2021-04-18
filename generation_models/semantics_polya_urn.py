import copy
import random

import dictionary_loader
import helper
from generation_models.general_model import GenModel


class PolyaUrnWithSemantics(GenModel):
    def __init__(self, name: str):
        parameters = copy.deepcopy(GenModel.params_general)
        parameters.update({
            'rho': {
                'value': 10,
                'constant': False
            },
            'nu': {
                'value': 5,
                'constant': False
            }
        })
        super().__init__(name, parameters)

    def generate(self) -> list:
        urn_initial_size = self.parameters['urn_initial_size']['value']
        desired_text_length = self.parameters['text_length']['value']
        rho = self.parameters['rho']['value']
        nu = self.parameters['nu']['value']

        # this list contains only types (unique words/symbols)
        # randomly extract specified number of words from the dictionary
        types_container = random.sample(dictionary_loader.dictionary_words, len(dictionary_loader.dictionary_words))

        urn_list = [key for key in types_container[:urn_initial_size]]
        dict_line = urn_initial_size

        out_unit_list = []  # contains a generated text as the list of units
        text_tokens: dict = {}  # contains all the types that are presented in current text

        for _ in helper.model_range(desired_text_length, desc=self.name):
            random_unit = random.choice(urn_list)
            out_unit_list.append(random_unit)

            if random_unit in text_tokens:
                text_tokens[random_unit] += rho

                for _ in range(rho):
                    urn_list.append(random_unit)
            else:
                # we should check the size of types_container in order to prevent the app from crash
                if dict_line > len(types_container) - nu:
                    helper.print_type_container_is_empty_message(desired_text_length, len(out_unit_list))
                    break