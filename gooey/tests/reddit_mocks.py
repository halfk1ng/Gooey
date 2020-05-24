import uuid
import weakref

class MockReddit:
    def __init__(self):
        self.user = MockUser()

class MockComment:
    def __init__(self, comment_id=None, author=None, body='test', parent=None):
        self.id = comment_id if comment_id else str(uuid.uuid1())
        self.author = author if author else MockUser()
        self.body = body
        self.replies = []
        self.parent = parent

    def reply(self, text):
        comment = MockComment(parent=self)
        self.replies.append(comment)
        return comment

class MockUser:
    def __init__(self, user_id=None, name='RedditGooeyBot'):
        self.id = user_id if user_id else str(uuid.uuid1())
        self.name = name

    def me(self):
        return self
