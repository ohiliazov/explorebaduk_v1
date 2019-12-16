from abc import ABCMeta, abstractmethod


class Message(metaclass=ABCMeta):
    def __init__(self, message_type: str, result: str):
        self.type = message_type
        self.result = result

    @abstractmethod
    def to_json(self):
        pass
