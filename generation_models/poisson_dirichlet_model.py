import random

import numpy as np

import vocabulary_loader
from generation_models.polya_urn import PolyaUrn
from helpers import helper


class PoissonDirechletModel(PolyaUrn):
    def __init__(self, name: str):
        super().__init__(name)
        self.param_conditions: dict = {
            'rho >= (nu + 1)': "{0}['rho']['value'] >= {0}['nu']['value'] + 1"
        }

    def generate(self) -> list:
        urn_initial_size = self.parameters['urn_initial_size']['value']
        desired_text_length = self.parameters['text_length']['value']
        rho = self.parameters['rho']['value']
        nu = self.parameters['nu']['value']
        new_rho = rho - nu - 1

        # this list contains only types (unique words/symbols)
        # types_container = vocabulary_loader.vocabulary_words.copy()
        types_container = list(range(len(vocabulary_loader.vocabulary_words)))
        max_types_index = len(types_container) - nu
        random.shuffle(types_container)

        urn_list = [key for key in types_container[:urn_initial_size]]
        urn_weights = np.array([1 for _ in range(len(urn_list))], dtype=np.int32)
        weights_sum = sum(urn_weights)
        weights_local = np.ones(nu + 1, dtype=np.int32)
        dict_line = urn_initial_size

        out_unit_list = []  # contains a generated text as the list of units
        text_tokens: set = set()  # contains all the types that are presented in current text

        for _ in helper.model_range(desired_text_length, desc=self.name):
            urn_index = helper.weighted_random(urn_weights, weights_sum)
            random_unit = urn_list[urn_index]
            out_unit_list.append(random_unit)

            if random_unit in text_tokens:
                urn_weights[urn_index] += rho
                weights_sum += rho
            else:
                # we should check the size of types_container in order to prevent the app from crash
                if dict_line > max_types_index:
                    helper.print_type_container_is_empty_message(desired_text_length, len(out_unit_list))
                    break

                text_tokens.add(random_unit)

                urn_weights[urn_index] += new_rho
                weights_sum += new_rho

                # update urn with totally new units taken from types_container
                for _ in range(nu + 1):
                    new_unit = types_container[dict_line]
                    dict_line += 1
                    urn_list.append(new_unit)
                urn_weights = np.concatenate((urn_weights, weights_local), axis=None)
                weights_sum += nu + 1

        types_container.clear()
        urn_list.clear()
        del urn_weights
        text_tokens.clear()

        return out_unit_list
