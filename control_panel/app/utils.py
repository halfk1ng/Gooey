import os
import json
import importlib
import inspect
import re

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

class FormNotFound(Exception):
    pass

class FormSelector:
    @staticmethod
    def select_form_for_bot_type(bot_type):
        config = BotConfigBuilder.load_bot_config()
        titleized_handler = ''.join(x.title() for x in config['handler'].split('_'))
        form_class = 'Edit{}BotForm'.format(titleized_handler)

        if form_class in FormSelector.available_forms():
            module = importlib.import_module('app.forms')
            form = getattr(module, form_class)
            return form
        else:
            raise FormNotFound('Form "{}" not found.'.format(form_class))

    @staticmethod
    def available_forms():
        import app.forms as Forms

        return [class_[0] for class_ in inspect.getmembers(Forms, inspect.isclass) if FormSelector.is_valid_form(class_)]

    def is_valid_form(class_):
        return bool(re.match(r'Edit.*BotForm', class_[0]))

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
            BotConfigBuilder.save_bot_config({})
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

        with open( os.path.abspath('./../VERSION'), 'r' ) as file:
            version = file.read()

        reddit_fields_dict['user_agent'] = 'Reddit bot /u/{} powered by Gooey v{}'.format(reddit_fields_dict['username'], version)

        return { 'reddit': reddit_fields_dict }

    @staticmethod
    def ignore_useless_keys(data):
        IGNORABLES = ['csrf_token', 'submit']

        for ignorable in IGNORABLES:
            data.pop(ignorable)