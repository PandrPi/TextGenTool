import copy
import json
import logging

default_settings = {
    "last_opened_file": {},
    "last_saved_file": {},
    "last_opened_folder": {},
    "sliding_window_points_number": 200,
    "sliding_window_step_divider": 6,
    "open_txt_file_with_plot_fitting_results": False
}


class Settings:
    _instance: 'Settings' = None
    settings_filename: str = 'settings.json'

    def __init__(self):
        self.__class__._instance = self
        self._settings_dict: dict = {}

        self._init_json(Settings.settings_filename)

    def _init_json(self, filename: str):
        settings_local = copy.deepcopy(default_settings)
        try:
            with open(filename, 'r') as fp:
                settings_local.update(json.load(fp))
        except Exception as e:
            logging.error(e)

        self._settings_dict = settings_local

    def _save_setting_to_file(self):
        try:
            with open(Settings.settings_filename, 'w') as fp:
                json.dump(self._settings_dict, fp, indent=4)
        except Exception as e:
            logging.error(e)

    @classmethod
    def get_value(cls, key: str):
        self = cls._instance
        if key not in self._settings_dict:
            return None
        return self._settings_dict[key]

    @classmethod
    def set_value(cls, key: str, value):
        self = cls._instance
        if key in self._settings_dict:
            self._settings_dict[key] = value
            self._save_setting_to_file()
