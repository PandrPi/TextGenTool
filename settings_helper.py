import json
import logging

default_settings = {
    "last_opened_file": {},
    "last_saved_file": {},
    "last_opened_folder": {}
}


class Settings:
    _instance: 'Settings' = None
    settings_filename: str = 'settings.json'

    def __init__(self):
        self.__class__._instance = self
        self._settings_dict: dict = {}

        self._init_json(Settings.settings_filename)

    def _init_json(self, filename: str):
        settings_local = default_settings
        try:
            with open(filename, 'r') as fp:
                settings_local = json.load(fp)
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
    def get_value(cls, key: str, extension: str = ''):
        self = cls._instance
        if key not in self._settings_dict:
            return None
        value = self._settings_dict[key]
        if extension not in value:
            return None
        return self._settings_dict[key][extension]

    @classmethod
    def set_value(cls, key: str, value, extension: str = ''):
        self = cls._instance
        if key in self._settings_dict:
            self._settings_dict[key][extension] = value
            self._save_setting_to_file()


settings = Settings()
