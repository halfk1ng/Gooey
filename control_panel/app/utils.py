import os
import json

VALID_FILENAMES = {
    'production': 'config.json',
    'development': 'config_development.json',
    'test': 'config_test.json'
}
CONFIG_FILENAME = VALID_FILENAMES[os.environ['FLASK_ENV']] if os.environ['FLASK_ENV'] in VALID_FILENAMES else VALID_FILENAMES['test']
CONFIG_PATH = os.path.abspath('./../{}'.format(CONFIG_FILENAME))
DEFAULT_INDENT = 2

class ConfigAlreadyExists(Exception):
    pass

class BotConfigBuilder:
    @staticmethod
    def build_new(form_data, override=False):
        bot_config = BotConfigBuilder.load_bot_config()

        if bot_config != {} and not override:
            raise ConfigAlreadyExists('Cannot overwrite existing bot configuration.')

        data = form_data.data.copy()
        BotConfigBuilder.ignore_useless_keys(data)
        bot_config = BotConfigBuilder.build_reddit_information(data)
        bot_config.update(data)
        
        BotConfigBuilder.save_bot_config(bot_config)

    @staticmethod
    def load_bot_config():
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as file:
                data = json.load(file)
        else:
            save_bot_config({})
            data = {}

        return data
        
    @staticmethod
    def save_bot_config(data):
        with open(CONFIG_PATH, 'w') as file:
            json.dump(data, file, indent=DEFAULT_INDENT)

    @staticmethod
    def build_reddit_information(data):
        REDDIT_FIELDS = ['username', 'password', 'client_id', 'client_secret']
        reddit_fields_dict = {}

        for field in REDDIT_FIELDS:
            reddit_fields_dict[field] = data.pop(field)

        return { 'reddit': reddit_fields_dict }

    @staticmethod
    def ignore_useless_keys(data):
        IGNORABLES = ['csrf_token', 'submit']

        for ignorable in IGNORABLES:
            data.pop(ignorable)