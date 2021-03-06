import time
import keyboard
from colorama import Fore


def __set_variable(var: list, value):
    var[0] = value


def choose(title: str, options: list) -> str:
    """
    Shows menu, where user can choose one of the presented options
    :param title: Menu title
    :param options: List of options
    :return: The option selected by user
    """
    selection_index = [0]
    should_return = []

    print(f"{Fore.GREEN + chr(9679)} {Fore.WHITE + title}")
    for i in range(0, len(options)):
        keyboard.add_hotkey(str(i + 1), lambda index=i: (
            selection_index.clear(), selection_index.append(index), should_return.append(True)))
        print(f" {Fore.GREEN + str(i + 1)}. {Fore.WHITE + options[i]}")

    while len(should_return) == 0:
        time.sleep(0.01)

    print(f"You choose option '{Fore.GREEN + str(selection_index[0] + 1) + Fore.WHITE}'", '\n')
    return options[selection_index[0]]
