import uuid

class TestReddit():
    def __init__(self):
        self.user = TestUser()

class TestComment():
    def __init__(self, comment_id=None, author=None, body='test', parent_limit=10):
        self.id = comment_id if comment_id else str(uuid.uuid1())
        self.author = author if author else TestUser()
        self.body = body

        if parent_limit > 0:
            self.parent = self.parent(parent_limit - 1)

    def reply(self, text):
        pass

    def parent(self, parent_limit):
        return TestComment(parent_limit=parent_limit)

class TestUser():
    def __init__(self, user_id=None, name='test'):
        self.id = user_id if user_id else str(uuid.uuid1())
        self.name = name

    def me(self):
        return self
