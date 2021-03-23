import easygui
import logging


class GenModel:
    params_general: dict = {
        'urn_initial_size': {
            'value': 10,
            'type': int,
            'constant': False
        },
        'text_length': {
            'value': 10,
            'type': int,
            'constant': False
        }
    }

    def __init__(self, name: str, parameters: dict):
        self.name = name
        self.parameters = parameters

    def __check_parameter(self, parameter: dict):
        def is_key_presented(key: str) -> bool:
            if key not in parameter:
                easygui.msgbox(f"{self.name} error: key '{key}' is not presented in parameters dict!",
                               title='Key is not presented!')
                return False
            return True

        try:
            all_keys_presented = is_key_presented('value') and is_key_presented('type') and is_key_presented('constant')
            parameter['value'] = parameter['type'](parameter['value'])  # manually convert value to desired type
            return all_keys_presented and isinstance(parameter['constant'], bool)
        except Exception as e:
            logging.exception(e)
            return False

    def verify_parameters(self):
        for param in self.parameters:
            self.__check_parameter(param)

    def generate(self):
        pass
