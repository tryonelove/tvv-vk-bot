from abc import ABC, abstractmethod
import requests

class Command(ABC):
    def __init__(self):
        self.session = requests.Session()

    @staticmethod
    def message(text=None, attachments=None):
        return {"message" : str(text), "attachments" : attachments}

    @abstractmethod
    def execute(self):
        pass