class GenModel:
    params_general: dict = {
        'urn_initial_size': {
            'value': 50,
            'constant': False
        },
        'text_length': {
            'value': 100000,
            'constant': False
        }
    }
    params_translation: dict = {
        'rho': 'ρ',
        'nu': 'ν',
        'eta': 'η'
    }

    def __init__(self, name: str, short_name: str, parameters: dict):
        self.name = name
        self.short_name = short_name
        self.parameters = parameters
        self.param_conditions: dict = {}

    def get_params_for_plot(self) -> dict:
        result = {}
        for k, v in self.parameters.items():
            if k not in self.params_general:
                result[GenModel.params_translation[k]] = v['value']
        return result

    def generate(self) -> (list, dict):
        pass
