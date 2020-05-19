from handlers.errors import FunctionNotAllowed, CommandNotMatched
from database.db import Database
import re
import sqlite3


class Economy():
    def __init__(self, reddit, config):
        self.reddit = reddit
        self.config = config
        self.action_kwargs = self.config['action']['kwargs']
        self.command_regex_template = '(?<={}\s).+'

        self.me = self.reddit.user.me()

        try:
            self.retrieve_user_inventory(self.reddit.user.me())
        except sqlite3.OperationalError:
            self.set_database_schema()

    def run(self):
        subreddit = self.config['subreddit']

        for comment in self.reddit.subreddit(subreddit).stream.comments(**self.action_kwargs):
            command = self.cmd_find_economy_command(comment)

            if command == None:
                continue
            else:
                self.cmd_call_command_function(comment, command)

    def format_command_regex(self, command_attributes):
        command_text = command_attributes['command_text']
        escaped_command = ''.join([self.escaped_character(character) for character in command_text])

        return self.command_regex_template.format(escaped_command)

    def escaped_character(self, character):
        # This method inherently disallows escaping space and newline
        if re.match(r'\w', character):
            return character

        return '\{}'.format(character)

    def find_command_value(self, command_attributes, text):
        try:
            regex = re.compile(self.format_command_regex(command_attributes))

            value = int(re.search(regex, text)[0])
        except (IndexError, ValueError) as e:
            raise CommandNotMatched('Regular expression error: {}'.format(e))

        return value

    def user_inventory_message(self, user):
        user_inventory = self.retrieve_user_inventory(user)
        items, funds = (user_inventory['items_available'], user_inventory['funds_available'])
        
        return 'Items Available: {}\n\nFunds Available: {}'.format(items, funds)

    def retrieve_user_inventory(self, user):
        db = Database()
        sql = 'SELECT * FROM economy_users WHERE economy_users.reddit_id = ?'
        user_record = db.connection.cursor().execute(sql, (user.id, )).fetchone()

        if user_record == None:
            self.set_blank_user_record(user)
            user_record = db.connection.cursor().execute(sql, (user.id, )).fetchone()

        db.close()

        return self.format_data(user_record)

    def store_changes(self, user, funds, transaction=0):
        db = Database()
        sql = """
            UPDATE economy_users
            SET items_available = items_available + ?, funds_available = funds_available + ?
            WHERE economy_users.reddit_id = ?
        """
        db.connection.cursor().execute(sql, (transaction, funds, user.id))
        db.connection.commit()
        db.close()

    def set_blank_user_record(self, user):
        db = Database()
        sql = """
            INSERT INTO economy_users (reddit_id)
            VALUES (?)
        """
        db.connection.cursor().execute(sql, (user.id, ))
        db.connection.commit()
        db.close()

    def set_database_schema(self):
        db = Database()
        sql = """
            CREATE TABLE IF NOT EXISTS economy_users (
                id integer PRIMARY KEY,
                reddit_id text NOT NULL UNIQUE,
                items_available integer NOT NULL DEFAULT 0,
                funds_available integer NOT NULL DEFAULT 0)
        """
        db.connection.cursor().execute(sql).fetchone()
        db.close()

    def format_data(self, data):
        db = Database()
        sql = 'SELECT * FROM economy_users LIMIT 1'
        column_names = db.connection.cursor().execute(sql).description
        db.close()

        d = {}
        for index in range(0, len(column_names)):
            column = column_names[index][0]
            value = data[index]

            d[column] = value

        return d
        
    def cmd_find_economy_command(self, comment):
        for command in self.config['economy_commands']:
            if 'case_sensitive' not in command.keys() or command['case_sensitive'] == False:
                command_text = command['text'].lower()
                comment_body = comment.body.lower()
            else:
                command_text = command['text']
                comment_body = comment.body

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

        current_funds = self.retrieve_user_inventory(user)['funds_available']

        if current_funds <= reload_threshold:
            current_funds += reload_amount
            self.store_changes(user, current_funds)
        
            inventory_text = self.user_inventory_message(user)
            comment.reply("{}'s funds were reloaded!\n\nCurrent inventory: {}".format(user.name, inventory_text))
        else:
            comment.reply("{}'s funds weren't reloaded due to being above the reload threshold.")

    def cmd_buy(self, comment, command_attributes):
        item_price = command_attributes['item_price']
        user = comment.author
        user_inventory = self.retrieve_user_inventory(user)['items_available']

        try:
            num_purchased = self.find_command_value(command_attributes)
        except CommandNotMatched:
            return 

        current_funds = user_inventory['funds_available']

        if current_funds >= item_price * num_purchased:
            current_funds -= num_purchased * item_price

            self.store_changes(user, current_funds, num_purchased)

            inventory_text = self.user_inventory_message(user)
            comment.reply("{}'s inventory has increased by {}, and funds decreased by {}!\n\nCurrent stats: {}".format(user.name, num_purchased, num_purchased * item_price, inventory_text))
        else:
            # TODO: Make a reply with no changes
            pass


    def cmd_sell(self, comment, command_attributes):
        item_price = command_attributes['item_price']
        user = comment.author
        user_inventory = self.retrieve_user_inventory(user)

        try:
            num_sold = self.find_command_value(command_attributes)
        except CommandNotMatched:
            return 

        if num_sold <= user_inventory['items_available']:
            current_funds = user_inventory['funds_available']
            current_funds += num_sold * item_price

            self.store_changes(user, current_funds, num_sold)

            inventory_text = self.user_inventory_message(user)
            comment.reply("{}'s inventory has decreased by {}, and funds increased by {}!\n\nCurrent stats: {}".format(user.name, num_sold, num_sold * item_price, inventory_text))
        else:
            # TODO: Make a reply with no changes
            pass

    def cmd_add(self, comment, command_attributes):
        user = comment.parent.author if command_attributes['award_to_parent'] == True else comment.author
        user_inventory = self.retrieve_user_inventory(user)

        current_amount = user_inventory['items_available'] + 1
        current_funds = user_inventory['funds_available']

        self.store_changes(user, current_funds, num_sold)
        inventory_text = self.user_inventory_message(user)
        comment.reply("{}'s inventory has increased by 1!\n\nCurrent stats: {}".format(user.name, inventory_text))

        if command_attributes['update_user_flair'] == True:
            self.cmd_set_user_flair_text(user, command_attributes)

    def cmd_list_inventory(self, comment, command_attributes):
        user = comment.author
        inventory = self.retrieve_user_inventory(user)

        comment.reply(self.user_inventory_message(user))

    def cmd_set_user_flair_text(self, user, command_attributes):
        raise NotImplementedError