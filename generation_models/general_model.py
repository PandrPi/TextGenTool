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

    def __init__(self, name: str, parameters: dict):
        self.name = name
        self.parameters = parameters
        self.param_conditions: dict = {}

    def generate(self) -> list:
        pass
