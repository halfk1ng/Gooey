import unittest
import sys
import os
import pdb
sys.path.append(os.path.abspath('../gooey/gooey'))
from handlers.economy import Economy
from database.db import Database
from tests.reddit_mocks import *


class TestEconomy(unittest.TestCase):

    os.environ['ENVIRONMENT'] = 'test'
    BASE_CONFIG = {
        'action': {
            'kwargs': {}
        }
    }
    DB_PATH = Database().select_db_path()

    def setUp(self):
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH) 

    def test_db_creation(self):
        # Should set up the DB if it doesn't exist already
        self.assertFalse(os.path.exists(self.DB_PATH))
        Economy(TestReddit(), self.BASE_CONFIG)
        self.assertTrue(os.path.exists(self.DB_PATH))

    def test_retrieve_user_inventory(self):
        # Should make a new record if one does not exist
        economy = Economy(TestReddit(), self.BASE_CONFIG)
        user = TestUser()
        sql = 'SELECT * FROM economy_users WHERE economy_users.reddit_id = ?'
        record = Database().connection.cursor().execute(sql, (user.id, )).fetchone()

        self.assertIsNone(record)
        blank_record = economy.retrieve_user_inventory(user)
        self.assertIsNotNone(blank_record)

    def test_cmd_reload_funds(self):
        # Should reload to the command setting
        command_attributes = {
            'reload_amount': 100,
            'reload_threshold': 99
        }
        user = TestUser()
        comment = TestComment(author=user)
        economy = Economy(TestReddit(), self.BASE_CONFIG)

        economy.cmd_reload_funds(comment, command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 100)

        # Should not reload if over the threshold
        economy.cmd_reload_funds(comment, command_attributes)

        inventory = economy.retrieve_user_inventory(user)

        self.assertEqual(inventory['funds_available'], 100)

    def test_cmd_buy(self):
        # Should purchase if the user has the funds available
        buy_command_attributes = {
            'text': '!buy',
            'item_price': 10
        }

        reload_command_attributes = {
            'reload_amount': 100,
            'reload_threshold': 1000000
        }

        user = TestUser()
        comment = TestComment(author=user, body='!buy 10')
        economy = Economy(TestReddit(), self.BASE_CONFIG)

        economy.cmd_reload_funds(comment, reload_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 100)
        self.assertEqual(inventory['items_available'], 0)

        economy.cmd_buy(comment, buy_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 10)

        # Should not allow purchase if no funds
        economy.cmd_buy(comment, buy_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 10)

    def test_cmd_sell(self):
        # Should sell if the user has the items available
        buy_command_attributes = {
            'text': '!buy',
            'item_price': 0
        }

        sell_command_attributes = {
            'text': '!sell',
            'item_price': 10
        }

        user = TestUser()
        buy_comment = TestComment(author=user, body='!buy 10')
        sell_comment = TestComment(author=user, body='!sell 10')
        economy = Economy(TestReddit(), self.BASE_CONFIG)

        economy.cmd_buy(buy_comment, buy_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 10)

        economy.cmd_sell(sell_comment, sell_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 100)
        self.assertEqual(inventory['items_available'], 0)

        # Should not allow sell if no items
        economy.cmd_sell(sell_comment, sell_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 100)
        self.assertEqual(inventory['items_available'], 0)

    def test_cmd_add(self):
        # Should add to comment user
        self_add_command_attributes = {
            'text': '!add'
        }

        user = TestUser()
        comment = TestComment(author=user, body='!add')
        economy = Economy(TestReddit(), self.BASE_CONFIG)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 0)

        economy.cmd_add(comment, self_add_command_attributes)

        inventory = economy.retrieve_user_inventory(user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 1)

        # Should add to comment parent user if 'award_to_parent' flag set
        parent_add_command_attributes = {
            'text': '!add',
            'award_to_parent': True
        }

        parent_user = comment.parent.author

        inventory = economy.retrieve_user_inventory(parent_user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 0)

        economy.cmd_add(comment, parent_add_command_attributes)

        inventory = economy.retrieve_user_inventory(parent_user)
        self.assertEqual(inventory['funds_available'], 0)
        self.assertEqual(inventory['items_available'], 1)
