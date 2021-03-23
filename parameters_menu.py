from colorama import Fore


def __write_input_request(var_name, value, end=''):
    import curses_helper
    curses_helper.write_formatted("  '{0, 2}' value ({1, 3}): " + end, var_name, value)


def complete(caption: str, parameters: dict):
    import curses_helper

    # write a caption
    curses_helper.write_formatted("{0, 2} {1, 1}\n", chr(9679), caption)
    previous_value_dict = {}

    # start parameters input loop
    for k, v in parameters.items():
        if not v['constant']:
            # we should check whether the user's input is correct
            while 1:
                __write_input_request(k, v['value'])
                value = curses_helper.read()
                if value == '':
                    value = str(v['value'])
                    curses_helper.move_line_home(-1)
                    __write_input_request(k, value, end=value + '\n')
                    break
                if not value.isnumeric():  # notify a user that input value is not correct
                    curses_helper.move_line_home(-1)

                    curses_helper.write_formatted("{0,4} {1,1}", chr(9679),
                                                  "Input value must be a positive integer number! Press Enter to try again.")
                    curses_helper.read()
                    curses_helper.move_line_home(-1)
                else:
                    break  # if the input is correct then break loop
            previous_value_dict[k] = str(v['value'])
            v['value'] = v['type'](value)
    curses_helper.close()

    #  print the same text without curses in order it to stay in console after the curses screen become closed

    green = Fore.GREEN
    white = Fore.WHITE

    #  write a caption
    print(f"\n{green + str(chr(9679)) + white} {caption}")
    for k, v in parameters.items():
        if not v['constant']:
            value = str(v['value'])
            print(f"  '{green + k + white}' value ({Fore.YELLOW + previous_value_dict[k] + white}): {value}")
