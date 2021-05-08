from helpers import helper, curses_helper
from generation_models.general_model import GenModel


def __write_input_request(var_name, value, end=''):
    curses_helper.write_formatted("  '{0, 2}' value ({1, 3}): " + end, var_name, value)


def complete(model: GenModel, error_message: str = ''):
    helper.flush_input()

    caption: str = f'Enter the parameters of the {model.name}:'
    parameters: dict = model.parameters

    # init curses_helper
    curses_helper.init()

    # write an error message if it exists
    curses_helper.write_formatted("{0}", error_message)

    # write a caption
    curses_helper.write_formatted("{0, 2} {1, 1}\n", chr(9679), caption)
    previous_value_dict = {}

    # start parameters input loop
    for k, v in parameters.items():
        if not v['constant']:
            # we should check whether the user's input is correct
            while 1:
                __write_input_request(k, v['value'])
                value = curses_helper.read(allow_single_dot=isinstance(v['value'], float))
                if value == '':
                    value = str(v['value'])
                    curses_helper.move_line_home(-1)
                    __write_input_request(k, value, end=value + '\n')
                    break
                # notify a user that input value is not correct
                if helper.safe_cast(value, int, None) is None and helper.safe_cast(value, float, None) is None:
                    curses_helper.move_line_home(-1)

                    curses_helper.write_formatted("{0,4} {1,1}", chr(9679),
                                                  "Input value must be a positive number! Press Enter to try again.")
                    curses_helper.read()
                    curses_helper.move_line_home(-1)
                else:
                    break  # if the input is correct then break loop
            previous_value_dict[k] = str(v['value'])
            v['value'] = type(v['value'])(value)
    curses_helper.close()

    for k, v in model.param_conditions.items():
        condition = v.format('model.parameters')
        if not eval(condition):
            return complete(model, "An error occurred while checking the conditions of the model parameters: \n"
                                   "\t{0}\n\n".format(k))
    return True
