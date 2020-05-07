from env import set_vars
import importlib
import json
from handlers.errors import HandlerNotAllowed
from handlers.config import load_config
import pdb
from reddit import reddit


class Bot():

    config = load_config('./config.json')

    def __init__(self):
        self.handler = self.select_handler()

    def select_handler(self):
        # TODO: Break allowed_handlers out into its own config file
        allowed_handlers = [
            'submission_stream'
        ]

        handler = 'handlers.{}'.format(self.config['handler'])
        if self.config['handler'] in allowed_handlers:
            class_ = ''.join(x.title() for x in self.config['handler'].split('_'))
            module = importlib.import_module(handler)
            handler_class = getattr(module, class_)
            return handler_class(reddit, self.config)
        else:
            raise HandlerNotAllowed('Handler "{}" not allowed'.format(handler))

    def start(self):
        self.handler.run()
        

Bot().start()