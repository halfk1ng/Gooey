from handlers.errors import FunctionNotAllowed
from database.db import Database
import sqlite3


class Economy():
    def __init__(self, reddit, config):
        self.reddit = reddit
        self.config = config
        self.action_kwargs = self.config['action']['kwargs']

        # I'm lazy, makes current user callable for db functions
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

    def retrieve_user_inventory(self, user, retries=0):
        db = Database()
        sql = 'SELECT * FROM economy_users WHERE economy_users.reddit_id = ?;'
        user_record = db.connection.cursor().execute(sql, (user.id, )).fetchone()

        if user_record == None and retries < 3:
            self.set_blank_user_record(user)
            user_record = self.retrieve_user_inventory(user, retries + 1)

        db.close()
        return self.format_data(user_record)

    def store_transactions(self, user, funds, transaction=0):
        db = Database()
        sql = """
            UPDATE economy_users
            SET items_available = items_available + ?, funds_available = funds_available + ?
            WHERE economy_users.reddit_id = ?;
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
                funds_available integer NOT NULL DEFAULT 0);
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

        if current_funds >= item_price * num_purchased:
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

    def cmd_add(self, comment, command_attributes):
        user = comment.parent.author if command_attributes['award_to_parent'] == True else comment.author
        user_inventory = self.retrieve_user_inventory(user)

        current_amount = user_inventory['available_items'] + 1
        current_funds = user_inventory['funds_available']

        self.store_changes(user, current_funds, num_sold)

        # TODO: Make a reply with changes

        if command_attributes['update_user_flair'] == True:
            self.cmd_set_user_flair_text(user, command_attributes)

    def cmd_list_inventory(self, comment, command_attributes):
        user = comment.author

        inventory = self.retrieve_user_inventory()

        # TODO: Make a reply with inventory

    def cmd_set_user_flair_text(self, user, command_attributes):
        raise NotImplementedError
