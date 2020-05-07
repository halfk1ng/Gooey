from handlers.errors import FunctionNotAllowed

class SubmissionStream():
    def __init__(self, reddit, config):
        self.reddit = reddit
        self.config = config

        self.action_kwargs = self.config['action']['kwargs']

        fn_name     = 'cmd_' + self.config['action']['name']
        self.fn     = getattr(self, fn_name)

        if self.fn is None:
            raise FunctionNotAllowed('Function "{}" not allowed'.format(fn_name))

    def run(self):
        subreddit = self.config['subreddit']
        
        for submission in self.reddit.subreddit(subreddit).stream.submissions(**self.action_kwargs):
            self.fn(submission)

    def cmd_print(self, submission):
        if submission.is_self:
            print(submission.selftext)
        else:
            print(submission.url)

    def f(self, **kwargs):
        print(kwargs)
        pass