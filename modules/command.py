from abc import ABC, abstractmethod
import requests


class Command(ABC):
    def __init__(self):
        self.session = requests.Session()

    @staticmethod
    def message(text=None, attachments=None):
        if isinstance(text, int):
            text = str(text)
        return {"message": text, "attachment": attachments}

    @abstractmethod
    def execute(self):
        pass
