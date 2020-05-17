from handlers.errors import FunctionNotAllowed


class CommentStream():
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
        
        for comment in self.reddit.subreddit(subreddit).stream.comments(**self.action_kwargs):
            self.fn(comment)

    def cmd_print(self, comment):
        print(comment.body)

    def cmd_reply(self, comment):
        comment.reply(self.config['comment_reply_body'])

    def cmd_add_user_flair(self, comment):
        if not self.config['comment_author_flair_condition']:
            return 

        redditor = comment.author
        attributes = self.config['comment_flair_attributes']
        redditor.mod.flair(attributes)

    def cmd_find_command(self, comment):
        for command in self.config['comment_commands']:
            if command['case_insensitive'] == True:
                command_text = command['text'].lower()
                comment_body = comment_body.lower()
            else:
                command_text = command['text']
                comment_body = comment_body

            if command_text in comment_body:
                self.cmd_call_command_function(comment, command)

    def cmd_call_command_function(self, comment, command_attributes):
        raise NotImplementedError