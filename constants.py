from colorama import Fore

# analysis menu consts
analysis_menu_title = "What do you want to do with generated text?"
analysis_menu_options = [
    "Show a plot of Zipf's law",
    "Show a plot of Heaps's law",
    "Show a plot of Taylor's law",
    "Save the calculated statistics to a file",
    "Save the generated text to a file",
]

# model selection menu consts
model_selection_menu_title = 'Which generation model do you want to use?'

# selection menu general consts
selection_menu_turn_back = 'Turn back'
selection_menu_start_over = 'Start over'
selection_menu_additional_options = [selection_menu_turn_back, selection_menu_start_over]

# dictionary consts
default_dictionary_path = 'dictionary_base/word_dictionary.json'
dictionary_menu_options = ['Use default full dictionary', 'Use custom dictionary (Should be chosen in dialog window)']
dictionary_menu_title = 'What dictionary do you want to use?'

# general model consts
model_generation_format = f'Generating text with {Fore.YELLOW}{{0}}{Fore.WHITE}'
