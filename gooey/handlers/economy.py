from handlers.errors import FunctionNotAllowed
from db import Database as db


class Economy():
    def __init__(self, reddit, config):
        self.reddit = reddit
        self.config = config

        self.action_kwargs = self.config['action']['kwargs']

    def run(self):
        subreddit = self.config['subreddit']
        
        for comment in self.reddit.subreddit(subreddit).stream.comments(**self.action_kwargs):
            command = self.cmd_find_economy_command(comment)

            if command == None:
                continue
            else:
                self.cmd_call_command_function(comment, command)

    def retrieve_user_inventory(self, user):
        pass

    def store_transactions(self, user, funds, transation=0):
        pass

    def cmd_find_economy_command(self, comment):
        for command in self.config['economy_commands']:
            if command['case_insensitive'] == True:
                command_text = command['text'].lower()
                comment_body = comment_body.lower()
            else:
                command_text = command['text']
                comment_body = comment_body

            if command_text in comment_body:
                return command
            
        return None

    def cmd_call_command_function(self, comment, command_attributes):
        command_name = command_attributes['function_name']
        fn_name = 'cmd_' + command_name
        self.fn = getattr(self, fn_name)

        if self.fn is None:
            raise FunctionNotAllowed('Function "{}" not allowed'.format(fn_name))

        self.fn(comment, command_attributes)

    def cmd_reload_funds(self, comment, command_attributes):
        reload_amount = command_attributes['reload_amount']
        reload_threshold = command_attributes['reload_threshold']
        user = comment.author

        current_funds = self.retrieve_user_inventory(user)

        if current_funds <= reload_threshold:
            current_funds += reload_amount

        self.store_changes(user, current_funds)

    def cmd_buy(self, comment, command_attributes):
        item_price = command_attributes['item_price']
        user = comment.author
        user_inventory = self.retrieve_user_inventory(user)

        # TODO: Make this a regex, find number purchased from comment
        num_purchased = 1
        current_funds = user_inventory['funds_available']

        if current_funds >= item_price * num_purchased
            current_funds -= num_purchased * item_price

            self.store_changes(user, current_funds, num_purchased)

            # TODO: Make a reply with changes
        else:
            # TODO: Make a reply with no changes
            pass


    def cmd_sell(self, comment, command_attributes):
        item_price = command_attributes['item_price']
        user = comment.author
        user_inventory = self.retrieve_user_inventory(user)

        # TODO: Make this a regex, find number sold from comment
        num_sold = 1

        if num_sold <= user_inventory['available_items']:
            current_funds = user_inventory['funds_available']
            current_funds += num_purchased * item_price

            self.store_changes(user, current_funds, num_sold)

            # TODO: Make a reply with changes
        else:
            # TODO: Make a reply with no changes
            pass

    def cmd_list_inventory(self, comment, command_attributes):
        user = comment.author

        inventory = self.retrieve_user_inventory()

        # TODO: Make a reply with inventory