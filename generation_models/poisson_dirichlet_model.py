import random

import dictionary_loader
import helper
from generation_models.polya_urn import PolyaUrn


class PoissonDirechletModel(PolyaUrn):
    def __init__(self, name: str):
        super().__init__(name)
        self.param_conditions: dict = {
            'rho > (nu - 1)': "{0}['rho']['value'] > {0}['nu']['value'] - 1"
        }

    def generate(self) -> list:
        urn_initial_size = self.parameters['urn_initial_size']['value']
        desired_text_length = self.parameters['text_length']['value']
        rho = self.parameters['rho']['value']
        nu = self.parameters['nu']['value']
        new_rho = rho - nu - 1

        # this list contains only types (unique words/symbols)
        types_container = random.sample(dictionary_loader.dictionary_words, 100000)

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
                if dict_line < len(types_container) - nu:
                    helper.print_type_container_is_empty_message(desired_text_length, len(out_unit_list))
                    break

                text_tokens[random_unit] = rho + 1

                for _ in range(new_rho):
                    urn_list.append(random_unit)

                # update urn with totally new units taken from types_container
                for _ in range(nu + 1):
                    new_unit = types_container[dict_line]
                    dict_line += 1
                    urn_list.append(new_unit)

        types_container.clear()
        urn_list.clear()
        text_tokens.clear()

        return out_unit_list
