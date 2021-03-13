import easygui


class GenModel:
    def __init__(self, name: str, variables: dict):
        self.name = name
        self.variables = variables

    def __check_variable(self, variable: dict):
        def is_key_presented(key: str) -> bool:
            if key not in variable:
                easygui.msgbox(f"{self.name} error: key '{key}' is not presented in variables dict!",
                               title='Key is not presented!')
                return False
            return True

        try:
            all_keys_presented = is_key_presented('value') and is_key_presented('type') and is_key_presented('constant')
            variable['value'] = variable['type'](variable['value'])  # manually convert value to desired type
            return all_keys_presented and isinstance(variable['constant'], bool)
        except Exception as e:
            print(e)
            return False

    def verify_variables(self):
        for var in self.variables:
            self.__check_variable(var)

    def generate(self):
        pass
