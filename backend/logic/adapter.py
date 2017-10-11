from chatterbot.conversation.statement import Statement
from chatterbot.logic import LogicAdapter


class Adapter1(LogicAdapter):
    def __init__(self, **kwargs):
        super(Adapter1, self).__init__(**kwargs)

    def can_process(self, statement):
        if "hello" in statement.text.split():
            return True
        return False

    def process(self, statement):
        confidence = 1
        response_statement = Statement("Hello from logic adapter")
        return confidence, response_statement
