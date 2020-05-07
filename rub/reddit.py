from env import set_vars
import os
import praw

set_vars()
reddit = praw.Reddit(username=os.environ['REDDIT_USERNAME'],
                     password=os.environ['REDDIT_PASSWORD'],
                     client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent=os.environ['REDDIT_USER_AGENT'])
