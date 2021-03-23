import random
import copy
import dictionary_loader
import helper
from generation_models.general_model import GenModel


class PolyaUrn(GenModel):
    def __init__(self, name: str):
        parameters = copy.deepcopy(GenModel.params_general)
        parameters.update({
            'rho': {
                'value': 4,
                'type': int,
                'constant': False
            },
            'nu': {
                'value': 4,
                'type': int,
                'constant': False
            }
        })
        parameters['text_length']['constant'] = True
        super().__init__(name, parameters)

    def generate(self):
        urn_initial_size = self.parameters['urn_initial_size']['value']
        desired_text_length = self.parameters['text_length']['value']
        rho = self.parameters['rho']['value']
        nu = self.parameters['nu']['value']

        # this list contains only types (unique words/symbols)
        # to prevent app from crashing we need to limit the k parameter of the choices method
        # by a total number of words/symbols
        types_container = random.choices(dictionary_loader.dictionary_words,
                                         k=min(desired_text_length * (nu + 1) + urn_initial_size,
                                               len(dictionary_loader.dictionary_words)))
        urn_dict = {key: 1 for key in types_container[:urn_initial_size]}
        urn_keys = set(urn_dict.keys())  # contains all the keys of unr dictionary
        # now we should exclude the urn_dict from the types_container
        types_container = set(types_container) - set(urn_keys)

        out_unit_list = []  # contains a generated text as the list of units
        text_types: set = set()  # contains all the types that are presented in current text

        for _ in helper.model_range(desired_text_length, desc=self.name):
            random_unit = urn_keys.pop()
            out_unit_list.append(random_unit)
            urn_keys.add(random_unit)

            if random_unit in text_types:
                urn_dict[random_unit] += rho
            else:
                # we should check the size of types_container in order to prevent the app from crash
                if len(types_container) < nu + 1:
                    helper.print_types_container_is_empty_message(desired_text_length, len(out_unit_list))
                    break

                urn_dict[random_unit] = rho
                # update urn with totally new units taken from types_container
                for _ in range(nu + 1):
                    new_unit = types_container.pop()
                    urn_dict[new_unit] = 1
                    urn_keys.add(new_unit)
                    text_types.add(new_unit)
                text_types.add(random_unit)
                urn_keys.add(random_unit)

        return out_unit_list
