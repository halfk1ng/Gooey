import logging


class Logger():
    def __init__(self, level_override=None):
        level = level_override if level_override else logging.INFO
        logging.basicConfig(filename='gooey.log', 
                            filemode='w', 
                            level=level,
                            format='%(asctime)s %(levelname)-1s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def log_function_call(self, function, attributes, submission=None, comment=None):
        if submission:
            post_type = 'submission'
            post_id = submission.id
        elif comment:
            post_type = 'comment'
            post_id = comment.id
        else:
            post_type = 'unknown type'
            post_id = 'N/A'

        msg = '{} called with attributes {} for {} ID {}'.format(function,
                                                                 attributes,
                                                                 post_type,
                                                                 post_id)

        logging.info(msg)
