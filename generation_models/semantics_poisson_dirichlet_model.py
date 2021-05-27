import random

import numpy as np

import vocabulary_loader
from generation_models.semantics_polya_urn import PolyaUrnWithSemantics
from helpers import helper


class PoissonDirechletModelWithSemantics(PolyaUrnWithSemantics):
    def __init__(self, name: str):
        super().__init__(name)
        self.param_conditions.update({
            'rho >= (nu + 1)': "{0}['rho']['value'] >= {0}['nu']['value'] + 1"
        })

    def generate(self) -> list:
        urn_initial_size = self.parameters['urn_initial_size']['value']
        desired_text_length = self.parameters['text_length']['value']
        rho = self.parameters['rho']['value']
        nu = self.parameters['nu']['value']
        eta = self.parameters['eta']['value']
        new_rho = rho - nu - 1

        # this list contains only types (unique words/symbols)
        # randomly extract specified number of words from the vocabulary
        # types_container = vocabulary_loader.vocabulary_words.copy()
        types_container = list(range(len(vocabulary_loader.vocabulary_words)))
        max_types_index = len(types_container) - nu
        random.shuffle(types_container)

        urn_list = [key for key in types_container[:urn_initial_size]]
        urn_weights = np.array([1 for _ in range(len(urn_list))], dtype=np.int32)
        normal_weights_sum = np.sum(urn_weights)
        weights_local = np.ones(nu + 1, dtype=np.int32)
        urn_indices = {urn_list[i]: i for i in range(len(urn_list))}
        dict_line = urn_initial_size

        initial_groups_number = urn_initial_size // (nu + 1)
        # share the elements of the urn_list uniformly among the initial labels
        labels = {i: set(urn_list.index(j) for j in urn_list[i::initial_groups_number]) for i in
                  range(initial_groups_number)}
        previous_label = initial_groups_number - 1
        label_origins = {i: None for i in range(initial_groups_number)}
        unit_labels = {}
        [unit_labels.update({urn_list[i]: k for i in v}) for k, v in labels.items()]
        eta_weights = np.empty(len(urn_list), dtype=np.float32)
        eta_weights.fill(eta)
        sum_of_multiplied_weights = helper.sum_of_multiplied_weights(urn_weights, normal_weights_sum, eta, np.empty(0))
        indices_of_one_weight: list = []

        out_unit_list = []  # contains a generated text as the list of units
        text_tokens: set = set()  # contains all the types that are presented in current text

        for _ in helper.model_range(desired_text_length, desc=self.name):
            urn_index = helper.weighted_random_with_etas(urn_weights, sum_of_multiplied_weights, eta_weights)
            random_unit = urn_list[urn_index]
            out_unit_list.append(random_unit)

            if random_unit in text_tokens:
                urn_weights[urn_index] += rho
                normal_weights_sum += rho
            else:
                # we should check the size of types_container in order to prevent the app from crash
                if dict_line > max_types_index:
                    helper.print_type_container_is_empty_message(desired_text_length, len(out_unit_list))
                    break

                text_tokens.add(random_unit)

                urn_weights[urn_index] += new_rho
                normal_weights_sum += new_rho

                current_label = previous_label + 1
                label_origins[current_label] = random_unit
                current_label_units = labels[current_label] = set()

                # update urn with totally new units taken from types_container
                for _ in range(nu + 1):
                    new_unit = types_container[dict_line]
                    dict_line += 1
                    urn_list.append(new_unit)

                    urn_index = len(urn_list) - 1
                    urn_indices[new_unit] = urn_index
                    indices_of_one_weight.append(urn_index)

                    unit_labels[new_unit] = current_label
                    current_label_units.add(urn_index)
                urn_weights = np.concatenate((urn_weights, weights_local), axis=None)
                normal_weights_sum += nu + 1
                previous_label = current_label

            # add the indices units that have the save label as the random_unit
            label_of_random_unit = unit_labels[random_unit]
            [indices_of_one_weight.append(i) for i in labels[label_of_random_unit]]
            # add a unit index that is the origin of the random_unit label
            origin_of_random_unit_label = label_origins[label_of_random_unit]
            if origin_of_random_unit_label is not None:
                indices_of_one_weight.append(urn_indices[origin_of_random_unit_label])
            # fill the list with the eta values
            indices_of_one_weight_array = np.array(indices_of_one_weight, dtype='int')
            eta_weights = helper.get_etas_array(eta, len(urn_weights), indices_of_one_weight_array)

            # in order to skip the difficult operation of multiplying urn_weights by eta_weights and finding the sum
            # of the elements of the resulting array, we want to calculate the sum in a much smarter and faster way.
            # This can be done by noting that only a few elements in the weight array have a value of 1.0, the other
            # elements have a value of eta.
            sum_of_multiplied_weights = helper.sum_of_multiplied_weights(urn_weights, normal_weights_sum, eta,
                                                                         indices_of_one_weight_array)

            indices_of_one_weight.clear()

        types_container.clear()
        urn_list.clear()
        del eta_weights
        del urn_weights
        urn_indices.clear()
        text_tokens.clear()

        return out_unit_list
