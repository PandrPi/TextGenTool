import copy
import random

import dictionary_loader
import helper
from generation_models.general_model import GenModel


class PolyaUrn(GenModel):
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
        urn_weights = [1 for _ in range(len(urn_list))]
        urn_indices_list = [i for i in range(len(urn_list))]
        weights_sum = sum(urn_weights)
        urn_indices = {urn_list[i]: i for i in range(len(urn_list))}
        dict_line = urn_initial_size

        out_unit_list = []  # contains a generated text as the list of units
        text_tokens: dict = {}  # contains all the types that are presented in current text

        from time import time
        time_sum = 0

        for _ in helper.model_range(desired_text_length, desc=self.name):
            start = time()
            random_unit = helper.weighted_random(urn_list, urn_weights, weights_sum)
            time_sum += time() - start
            out_unit_list.append(random_unit)

            if random_unit in text_tokens:
                text_tokens[random_unit] += rho

                urn_index = urn_indices[random_unit]
                urn_weights[urn_index] += rho
                weights_sum += rho

                # for _ in range(rho):
                #     urn_list.append(random_unit)
            else:
                # we should check the size of types_container in order to prevent the app from crash
                if dict_line > len(types_container) - nu:
                    helper.print_type_container_is_empty_message(desired_text_length, len(out_unit_list))
                    break

                text_tokens[random_unit] = rho + 1

                urn_index = urn_indices[random_unit]
                urn_weights[urn_index] += rho
                weights_sum += rho

                # update urn with totally new units taken from types_container
                for _ in range(nu + 1):
                    new_unit = types_container[dict_line]
                    dict_line += 1
                    urn_list.append(new_unit)

                    urn_weights.append(1)
                    weights_sum += 1
                    urn_index = len(urn_list) - 1
                    urn_indices[new_unit] = urn_index
                    urn_indices_list.append(urn_index)

        types_container.clear()
        urn_list.clear()
        text_tokens.clear()

        print(time_sum)

        return out_unit_list
